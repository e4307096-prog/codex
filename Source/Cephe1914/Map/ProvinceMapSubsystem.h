#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "Core/CepheTypes.h"
#include "Core/CepheData.h"
#include "ProvinceMapSubsystem.generated.h"

class UTexture2D;
class UDataTable;

DECLARE_MULTICAST_DELEGATE_OneParam(FOnProvinceHovered, int32 /*ProvinceId*/);
DECLARE_MULTICAST_DELEGATE_OneParam(FOnProvinceSelected, int32 /*ProvinceId, 0 = secim yok*/);
DECLARE_MULTICAST_DELEGATE_OneParam(FOnArmySelected, int32 /*ArmyIndex, -1 = yok*/);
DECLARE_MULTICAST_DELEGATE_OneParam(FOnMapModeChanged, EMapMode);

/**
 * Harita verisi: ID dokusu (CPU), DataTable'lar, JSON'lar ve 1024x4 arama dokusu.
 * Arama dokusu sutunu = bolge kimligi. Ulke indeksi = DT_Nations satir sirasi + 1 (0 = yok).
 */
UCLASS()
class CEPHE1914_API UProvinceMapSubsystem : public UWorldSubsystem
{
	GENERATED_BODY()

public:
	virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
	virtual void Deinitialize() override;

	/** Tembel yukleme: her tuketici BeginPlay'de cagirir. */
	void EnsureLoaded();
	bool IsLoaded() const { return bLoaded; }

	int32 GetProvinceAtUV(FVector2D UV) const;
	int32 GetProvinceAtWorld(FVector WorldPos) const;

	const FProvinceRow* FindProvince(int32 Id) const;
	const FNationRow* FindNation(const FString& Code) const;
	FLinearColor GetNationColor(const FString& Code) const;
	ESide GetSideOfNation(const FString& Code) const;
	const TArray<FFrontLine>& GetFronts() const { return Fronts; }
	const TArray<FRailLine>& GetRails() const { return Rails; }
	const TArray<FArmyRecord>& GetArmies() const { return Armies; }
	const TArray<int32>* GetNeighbors(int32 Id) const { return Neighbors.Find(Id); }
	int32 GetTrenchLevel(int32 Id) const { const uint8* T = TrenchByProvince.Find(Id); return T ? *T : 0; }

	UTexture2D* GetLookupTexture() const { return LookupTexture; }

	EMapMode GetMapMode() const { return MapMode; }
	void SetMapMode(EMapMode NewMode);

	int32 GetHoveredProvince() const { return HoveredProvince; }
	int32 GetSelectedProvince() const { return SelectedProvince; }
	int32 GetSelectedArmy() const { return SelectedArmy; }
	void SetHoveredProvince(int32 Id);
	void SelectProvince(int32 Id);
	void SelectArmy(int32 ArmyIndex);

	FOnProvinceHovered OnProvinceHovered;
	FOnProvinceSelected OnProvinceSelected;
	FOnArmySelected OnArmySelected;
	FOnMapModeChanged OnMapModeChanged;

	FString ProvincesTablePath = TEXT("/Game/Map/DT_Provinces.DT_Provinces");
	FString NationsTablePath = TEXT("/Game/Map/DT_Nations.DT_Nations");

private:
	bool LoadIdTexture();
	void LoadTables();
	void BuildDerivedData();
	void CreateLookupTexture();
	void RebuildLookup();
	FLinearColor ModeColor(const FProvinceRow& P) const;
	uint8 NationIndex(const FString& Code) const;

	bool bLoaded = false;
	EMapMode MapMode = EMapMode::Political;
	int32 HoveredProvince = 0;
	int32 SelectedProvince = 0;
	int32 SelectedArmy = -1;

	int32 IdWidth = 0;
	int32 IdHeight = 0;
	TArray<uint16> IdMap;

	UPROPERTY() TObjectPtr<UTexture2D> LookupTexture;
	UPROPERTY() TObjectPtr<UDataTable> ProvinceTable;
	UPROPERTY() TObjectPtr<UDataTable> NationTable;

	TMap<int32, FProvinceRow> Provinces;
	TArray<FNationRow> Nations;
	TMap<FString, int32> NationLookup;
	TArray<FFrontLine> Fronts;
	TArray<FRailLine> Rails;
	TArray<FArmyRecord> Armies;
	TArray<FAdjacencyEdge> Adjacency;
	TMap<int32, TArray<int32>> Neighbors;
	TMap<int32, uint8> TrenchByProvince;
	TSet<int32> FrontierProvinces;

	TArray<FColor> Pixels;
};
