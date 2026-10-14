#include "Map/ProvinceMapActor.h"
#include "Map/ProvinceMapSubsystem.h"
#include "Cephe1914.h"
#include "Core/CepheUtil.h"
#include "Game/CephePlayerController.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/Texture.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"

AProvinceMapActor::AProvinceMapActor()
{
	PrimaryActorTick.bCanEverTick = true;

	BoardMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BoardMesh"));
	SetRootComponent(BoardMesh);
	BoardMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	BoardMeshAsset = TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Map/Meshes/SM_MapBoard.SM_MapBoard")));
	MapMaterialAsset = TSoftObjectPtr<UMaterialInterface>(FSoftObjectPath(TEXT("/Game/Map/M_ProvinceMap.M_ProvinceMap")));
	IdTextureAsset = TSoftObjectPtr<UTexture>(FSoftObjectPath(TEXT("/Game/Map/T_ProvinceId.T_ProvinceId")));
	HeightTextureAsset = TSoftObjectPtr<UTexture>(FSoftObjectPath(TEXT("/Game/Map/T_Heightmap.T_Heightmap")));
	PaperTextureAsset = TSoftObjectPtr<UTexture>(FSoftObjectPath(TEXT("/Game/Map/T_Paper.T_Paper")));
}

void AProvinceMapActor::BeginPlay()
{
	Super::BeginPlay();

	Map = GetWorld()->GetSubsystem<UProvinceMapSubsystem>();
	if (Map.IsValid())
	{
		Map->EnsureLoaded();
		Map->OnMapModeChanged.AddUObject(this, &AProvinceMapActor::HandleMapMode);
	}

	UStaticMesh* Mesh = BoardMeshAsset.LoadSynchronous();
	if (!Mesh)
	{
		UE_LOG(LogCephe, Warning, TEXT("SM_MapBoard yok, duz levha kullaniliyor"));
		Mesh = CepheUtil::LoadQuiet<UStaticMesh>(TEXT("/Engine/BasicShapes/Plane.Plane"));
		BoardMesh->SetRelativeScale3D(FVector(CepheMap::WidthCm / 100.0, CepheMap::HeightCm / 100.0, 1.0));
	}
	BoardMesh->SetStaticMesh(Mesh);

	ApplyMaterialParams();
}

void AProvinceMapActor::EndPlay(const EEndPlayReason::Type Reason)
{
	if (Map.IsValid())
	{
		Map->OnMapModeChanged.RemoveAll(this);
	}
	Super::EndPlay(Reason);
}

void AProvinceMapActor::ApplyMaterialParams()
{
	UMaterialInterface* Parent = MapMaterialAsset.LoadSynchronous();
	if (!Parent)
	{
		UE_LOG(LogCephe, Warning, TEXT("M_ProvinceMap yuklenemedi"));
		return;
	}
	Material = UMaterialInstanceDynamic::Create(Parent, this);
	BoardMesh->SetMaterial(0, Material);

	if (UTexture* T = IdTextureAsset.LoadSynchronous()) Material->SetTextureParameterValue(TEXT("IdTex"), T);
	if (UTexture* T = HeightTextureAsset.LoadSynchronous()) Material->SetTextureParameterValue(TEXT("HeightTex"), T);
	if (UTexture* T = PaperTextureAsset.LoadSynchronous()) Material->SetTextureParameterValue(TEXT("PaperTex"), T);
	if (Map.IsValid() && Map->GetLookupTexture())
	{
		Material->SetTextureParameterValue(TEXT("LookupTex"), Map->GetLookupTexture());
	}
	Material->SetVectorParameterValue(TEXT("MapTexelSize"), FLinearColor(1.f / 4096.f, 1.f / 3112.f, 0.f, 0.f));
	Material->SetVectorParameterValue(TEXT("BorderColor"), BorderColor);
	Material->SetVectorParameterValue(TEXT("NationBorderColor"), NationBorderColor);
	Material->SetVectorParameterValue(TEXT("SeaColor"), SeaColor);
	Material->SetScalarParameterValue(TEXT("HillshadeStrength"), HillshadeStrength);
	HandleMapMode(Map.IsValid() ? Map->GetMapMode() : EMapMode::Political);
}

void AProvinceMapActor::HandleMapMode(EMapMode Mode)
{
	if (Material)
	{
		Material->SetScalarParameterValue(TEXT("MapMode"), static_cast<float>(static_cast<uint8>(Mode)));
	}
}

void AProvinceMapActor::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!Map.IsValid()) return;

	ACephePlayerController* PC = Cast<ACephePlayerController>(GetWorld()->GetFirstPlayerController());
	if (!PC) return;
	if (PC->IsPointerOverUI())
	{
		Map->SetHoveredProvince(0);
		return;
	}

	FVector Origin, Dir;
	int32 Id = 0;
	if (PC->DeprojectMousePositionToWorld(Origin, Dir) && FMath::Abs(Dir.Z) > KINDA_SMALL_NUMBER)
	{
		const double T = (HoverPlaneZ - Origin.Z) / Dir.Z; // isin - Z = HoverPlaneZ duzlemi kesisimi
		if (T > 0.0)
		{
			Id = Map->GetProvinceAtWorld(Origin + Dir * T);
		}
	}
	Map->SetHoveredProvince(Id);
}
