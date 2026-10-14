#include "Map/ProvinceMapSubsystem.h"
#include "Cephe1914.h"
#include "Engine/DataTable.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "TextureResource.h"
#include "IImageWrapper.h"
#include "IImageWrapperModule.h"
#include "Modules/ModuleManager.h"
#include "Misc/FileHelper.h"
#include "UObject/SoftObjectPtr.h"

bool UProvinceMapSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
	const UWorld* W = Cast<UWorld>(Outer);
	return W && W->IsGameWorld() && Super::ShouldCreateSubsystem(Outer);
}

void UProvinceMapSubsystem::Deinitialize()
{
	LookupTexture = nullptr;
	IdMap.Empty();
	Super::Deinitialize();
}

void UProvinceMapSubsystem::EnsureLoaded()
{
	if (bLoaded) return;
	bLoaded = true;

	LoadTables();
	LoadIdTexture();
	CepheData::LoadFronts(Fronts);
	CepheData::LoadRails(Rails);
	CepheData::LoadArmies(Armies);
	CepheData::LoadAdjacency(Adjacency);
	BuildDerivedData();
	CreateLookupTexture();
	RebuildLookup();
	UE_LOG(LogCephe, Log, TEXT("Harita yuklendi: %d bolge, %d ulke, %d cephe, %d demiryolu, %d ordu"),
	       Provinces.Num(), Nations.Num(), Fronts.Num(), Rails.Num(), Armies.Num());
}

bool UProvinceMapSubsystem::LoadIdTexture()
{
	TArray<uint8> File;
	const FString Path = CepheData::RawPath(TEXT("province_id.png"));
	if (!FFileHelper::LoadFileToArray(File, *Path))
	{
		UE_LOG(LogCephe, Warning, TEXT("province_id.png okunamadi: %s"), *Path);
		return false;
	}
	IImageWrapperModule& Module = FModuleManager::LoadModuleChecked<IImageWrapperModule>(TEXT("ImageWrapper"));
	TSharedPtr<IImageWrapper> Wrapper = Module.CreateImageWrapper(EImageFormat::PNG);
	if (!Wrapper.IsValid() || !Wrapper->SetCompressed(File.GetData(), File.Num()))
	{
		UE_LOG(LogCephe, Warning, TEXT("province_id.png cozulemedi"));
		return false;
	}
	IdWidth = Wrapper->GetWidth();
	IdHeight = Wrapper->GetHeight();
	TArray64<uint8> Raw;
	if (!Wrapper->GetRaw(ERGBFormat::RGBA, 8, Raw))
	{
		UE_LOG(LogCephe, Warning, TEXT("province_id.png ham veri alinamadi"));
		IdWidth = IdHeight = 0;
		return false;
	}
	const int64 Count = static_cast<int64>(IdWidth) * IdHeight;
	IdMap.SetNumUninitialized(static_cast<int32>(Count));
	const uint8* Src = Raw.GetData();
	for (int64 i = 0; i < Count; ++i)
	{
		IdMap[static_cast<int32>(i)] = static_cast<uint16>(Src[i * 4] + Src[i * 4 + 1] * 256); // id = R + G*256
	}
	return true;
}

void UProvinceMapSubsystem::LoadTables()
{
	ProvinceTable = TSoftObjectPtr<UDataTable>(FSoftObjectPath(ProvincesTablePath)).LoadSynchronous();
	NationTable = TSoftObjectPtr<UDataTable>(FSoftObjectPath(NationsTablePath)).LoadSynchronous();

	if (NationTable)
	{
		for (const FName& RowName : NationTable->GetRowNames())
		{
			if (const FNationRow* R = NationTable->FindRow<FNationRow>(RowName, TEXT("Nations")))
			{
				NationLookup.Add(R->Code, Nations.Num());
				Nations.Add(*R);
			}
		}
	}
	else
	{
		UE_LOG(LogCephe, Warning, TEXT("DT_Nations yuklenemedi: %s"), *NationsTablePath);
	}

	if (ProvinceTable)
	{
		for (const FName& RowName : ProvinceTable->GetRowNames())
		{
			if (const FProvinceRow* R = ProvinceTable->FindRow<FProvinceRow>(RowName, TEXT("Provinces")))
			{
				Provinces.Add(R->Id, *R);
			}
		}
	}
	else
	{
		UE_LOG(LogCephe, Warning, TEXT("DT_Provinces yuklenemedi: %s"), *ProvincesTablePath);
	}
}

void UProvinceMapSubsystem::BuildDerivedData()
{
	for (const FAdjacencyEdge& E : Adjacency)
	{
		Neighbors.FindOrAdd(E.A).AddUnique(E.B);
		Neighbors.FindOrAdd(E.B).AddUnique(E.A);

		const FProvinceRow* PA = FindProvince(E.A);
		const FProvinceRow* PB = FindProvince(E.B);
		if (PA && PB)
		{
			const ESide SA = GetSideOfNation(PA->Controller);
			const ESide SB = GetSideOfNation(PB->Controller);
			if (SA != ESide::Neutral && SB != ESide::Neutral && SA != SB)
			{
				FrontierProvinces.Add(E.A);
				FrontierProvinces.Add(E.B);
			}
		}
	}
	for (const FFrontLine& F : Fronts)
	{
		const uint8 Lvl = static_cast<uint8>(F.Trench);
		uint8& A = TrenchByProvince.FindOrAdd(F.A);
		A = FMath::Max(A, Lvl);
		uint8& B = TrenchByProvince.FindOrAdd(F.B);
		B = FMath::Max(B, Lvl);
		FrontierProvinces.Add(F.A);
		FrontierProvinces.Add(F.B);
	}
}

void UProvinceMapSubsystem::CreateLookupTexture()
{
	LookupTexture = UTexture2D::CreateTransient(CepheMap::LookupWidth, CepheMap::LookupHeight, PF_B8G8R8A8);
	if (!LookupTexture) return;
	LookupTexture->Filter = TF_Nearest;
	LookupTexture->SRGB = false;
	LookupTexture->AddressX = TA_Clamp;
	LookupTexture->AddressY = TA_Clamp;
	LookupTexture->CompressionSettings = TC_VectorDisplacementmap;
	LookupTexture->LODGroup = TEXTUREGROUP_Pixels2D;
	LookupTexture->NeverStream = true;
#if WITH_EDITORONLY_DATA
	LookupTexture->MipGenSettings = TMGS_NoMipmaps;
#endif
	LookupTexture->UpdateResource();
}

const FProvinceRow* UProvinceMapSubsystem::FindProvince(int32 Id) const
{
	return Provinces.Find(Id);
}

const FNationRow* UProvinceMapSubsystem::FindNation(const FString& Code) const
{
	const int32* Idx = NationLookup.Find(Code);
	return Idx ? &Nations[*Idx] : nullptr;
}

FLinearColor UProvinceMapSubsystem::GetNationColor(const FString& Code) const
{
	const FNationRow* N = FindNation(Code);
	return N ? N->Color : FLinearColor(0.5f, 0.5f, 0.5f, 1.f);
}

ESide UProvinceMapSubsystem::GetSideOfNation(const FString& Code) const
{
	const FNationRow* N = FindNation(Code);
	return N ? N->Side : ESide::Neutral;
}

uint8 UProvinceMapSubsystem::NationIndex(const FString& Code) const
{
	const int32* Idx = NationLookup.Find(Code);
	return Idx ? static_cast<uint8>(FMath::Min(*Idx + 1, 255)) : 0;
}

int32 UProvinceMapSubsystem::GetProvinceAtUV(FVector2D UV) const
{
	if (IdMap.Num() == 0 || UV.X < 0.0 || UV.Y < 0.0 || UV.X >= 1.0 || UV.Y >= 1.0) return 0;
	const int32 X = FMath::Clamp(FMath::FloorToInt(UV.X * IdWidth), 0, IdWidth - 1);
	const int32 Y = FMath::Clamp(FMath::FloorToInt(UV.Y * IdHeight), 0, IdHeight - 1);
	return IdMap[Y * IdWidth + X];
}

int32 UProvinceMapSubsystem::GetProvinceAtWorld(FVector WorldPos) const
{
	return GetProvinceAtUV(CepheMap::WorldToUV(WorldPos));
}

FLinearColor UProvinceMapSubsystem::ModeColor(const FProvinceRow& P) const
{
	switch (MapMode)
	{
	case EMapMode::Political:
		return GetNationColor(P.Controller);
	case EMapMode::Alliance:
	{
		switch (GetSideOfNation(P.Controller))
		{
		case ESide::Entente: return FLinearColor(0.22f, 0.32f, 0.58f);
		case ESide::Central: return FLinearColor(0.62f, 0.48f, 0.26f);
		default: return FLinearColor(0.74f, 0.71f, 0.60f);
		}
	}
	case EMapMode::Front:
	{
		FLinearColor C;
		switch (GetSideOfNation(P.Controller))
		{
		case ESide::Entente: C = FLinearColor(0.30f, 0.38f, 0.55f); break;
		case ESide::Central: C = FLinearColor(0.55f, 0.47f, 0.32f); break;
		default: C = FLinearColor(0.70f, 0.68f, 0.60f); break;
		}
		if (FrontierProvinces.Contains(P.Id)) C = FMath::Lerp(C, FLinearColor(0.75f, 0.15f, 0.10f), 0.55f);
		return C;
	}
	case EMapMode::Terrain:
	default:
		switch (P.Terrain)
		{
		case ETerrain::Forest: return FLinearColor(0.30f, 0.45f, 0.26f);
		case ETerrain::Hills: return FLinearColor(0.58f, 0.48f, 0.32f);
		case ETerrain::Mountains: return FLinearColor(0.48f, 0.45f, 0.43f);
		case ETerrain::Marsh: return FLinearColor(0.42f, 0.52f, 0.47f);
		default: return FLinearColor(0.76f, 0.72f, 0.52f);
		}
	}
}

void UProvinceMapSubsystem::RebuildLookup()
{
	if (!LookupTexture) return;
	const int32 W = CepheMap::LookupWidth;
	Pixels.Init(FColor(0, 0, 0, 255), W * CepheMap::LookupHeight);

	// Id 0 = deniz: renk satiri 0'da, gerisi bos.
	Pixels[0] = FColor(30, 50, 60, 255);

	for (const TPair<int32, FProvinceRow>& Pair : Provinces)
	{
		const int32 Id = Pair.Key;
		if (Id <= 0 || Id >= W) continue;
		const FProvinceRow& P = Pair.Value;

		// Satir 0: dokuya sRGB kapali yazildigi icin dogrusal deger oldugu gibi kodlanir.
		Pixels[Id] = ModeColor(P).ToFColor(false);
		// Satir 1: sahip, kontrol eden, taraf.
		Pixels[W + Id] = FColor(NationIndex(P.Owner), NationIndex(P.Controller),
		                        static_cast<uint8>(GetSideOfNation(P.Controller)), 255);
		// Satir 2: secili, ustunde, isgal, kale.
		const bool bSel = (Id == SelectedProvince);
		const bool bHov = (Id == HoveredProvince);
		const bool bOcc = (P.Owner != P.Controller);
		Pixels[2 * W + Id] = FColor(bSel ? 255 : 0, bHov ? 255 : 0, bOcc ? 255 : 0, P.Fort ? 255 : 0);
		// Satir 3: siper x51, arazi x51.
		const uint8* Tr = TrenchByProvince.Find(Id);
		Pixels[3 * W + Id] = FColor(static_cast<uint8>((Tr ? *Tr : 0) * 51),
		                            static_cast<uint8>(static_cast<int32>(P.Terrain) * 51), 0, 0);
	}

	FTexturePlatformData* PD = LookupTexture->GetPlatformData();
	if (!PD || PD->Mips.Num() == 0) return;
	FTexture2DMipMap& Mip = PD->Mips[0];
	void* Data = Mip.BulkData.Lock(LOCK_READ_WRITE);
	FMemory::Memcpy(Data, Pixels.GetData(), Pixels.Num() * sizeof(FColor));
	Mip.BulkData.Unlock();
	LookupTexture->UpdateResource();
}

void UProvinceMapSubsystem::SetMapMode(EMapMode NewMode)
{
	if (NewMode == MapMode) return;
	MapMode = NewMode;
	RebuildLookup();
	OnMapModeChanged.Broadcast(MapMode);
}

void UProvinceMapSubsystem::SetHoveredProvince(int32 Id)
{
	if (Id == HoveredProvince) return;
	HoveredProvince = Id;
	RebuildLookup();
	OnProvinceHovered.Broadcast(Id);
}

void UProvinceMapSubsystem::SelectProvince(int32 Id)
{
	const bool bHadArmy = SelectedArmy >= 0;
	SelectedArmy = -1;
	SelectedProvince = Id;
	RebuildLookup();
	if (bHadArmy) OnArmySelected.Broadcast(-1);
	OnProvinceSelected.Broadcast(Id);
}

void UProvinceMapSubsystem::SelectArmy(int32 ArmyIndex)
{
	if (!Armies.IsValidIndex(ArmyIndex)) return;
	SelectedArmy = ArmyIndex;
	SelectedProvince = Armies[ArmyIndex].Province; // haritada bolgeyi vurgula, panel orduyu gosterir
	RebuildLookup();
	OnArmySelected.Broadcast(ArmyIndex);
}
