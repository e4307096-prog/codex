#pragma once

#include "CoreMinimal.h"
#include "UObject/UObjectGlobals.h"

class AActor;
class UMeshComponent;
class UMaterialInterface;
class UMaterialInstanceDynamic;
class UStaticMesh;

namespace CepheUtil
{
	/** Yoksa sessizce nullptr doner (uyari basmaz). */
	template <class T>
	T* LoadQuiet(const TCHAR* Path)
	{
		return LoadObject<T>(nullptr, Path, nullptr, LOAD_NoWarn | LOAD_Quiet);
	}

	/** Bilesenin Slot malzemesinden (veya Override'dan) dinamik malzeme uretip Param vektorunu boyar. */
	CEPHE1914_API UMaterialInstanceDynamic* TintSlot(UMeshComponent* Comp, int32 Slot, UMaterialInterface* Override,
	                                                 FName Param, const FLinearColor& Color);

	/**
	 * WorldPts noktalarindan USplineComponent kurar ve her aralik icin USplineMeshComponent uretir.
	 * Mesh X ekseni boyunca uzatilir. MID verilirse tum parcalara atanir.
	 */
	CEPHE1914_API void BuildSplineStrip(AActor* Owner, const TArray<FVector>& WorldPts, UStaticMesh* Mesh,
	                                    UMaterialInterface* Material, float WidthScale, float MinStepCm);
}
