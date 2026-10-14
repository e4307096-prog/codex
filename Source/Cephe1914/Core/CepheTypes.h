#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "CepheTypes.generated.h"

UENUM(BlueprintType)
enum class EMapMode : uint8
{
	Political,
	Alliance,
	Front,
	Terrain
};

/** Arama dokusu satir 1 B kanali: 0 tarafsiz, 1 Itilaf, 2 Ittifak (siralama bu degerlere esit). */
UENUM(BlueprintType)
enum class ESide : uint8
{
	Neutral,
	Entente,
	Central
};

UENUM(BlueprintType)
enum class ETerrain : uint8
{
	Plains,
	Forest,
	Hills,
	Mountains,
	Marsh
};

/** provinces.csv satiri: ---,Id,Name,Owner,Controller,Terrain,Fort,Population,Industry,CentroidU,CentroidV */
USTRUCT(BlueprintType)
struct FProvinceRow : public FTableRowBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 Id = 0;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FString Name;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FString Owner;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FString Controller;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) ETerrain Terrain = ETerrain::Plains;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) bool Fort = false;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float Population = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float Industry = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float CentroidU = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) float CentroidV = 0.f;
};

/** nations.csv satiri: ---,Code,Name,Side,Color */
USTRUCT(BlueprintType)
struct FNationRow : public FTableRowBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite) FString Code;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FString Name;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) ESide Side = ESide::Neutral;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FLinearColor Color = FLinearColor::White;
};

/** Dunya olcegi (teknik sozlesme): levha 40960 x 31120 cm, merkez orijin, UV(0,0) sol ust. */
namespace CepheMap
{
	constexpr double WidthCm = 40960.0;
	constexpr double HeightCm = 31120.0;
	constexpr int32 LookupWidth = 1024;
	constexpr int32 LookupHeight = 4;

	FORCEINLINE FVector UVToWorld(const FVector2D& UV, double Z = 0.0)
	{
		return FVector(-WidthCm * 0.5 + UV.X * WidthCm, -HeightCm * 0.5 + UV.Y * HeightCm, Z);
	}

	FORCEINLINE FVector2D WorldToUV(const FVector& W)
	{
		return FVector2D((W.X + WidthCm * 0.5) / WidthCm, (W.Y + HeightCm * 0.5) / HeightCm);
	}
}
