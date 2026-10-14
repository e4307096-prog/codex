#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ArmyCounterActor.generated.h"

class UStaticMeshComponent;
class UMaterialInstanceDynamic;
class UMaterialInterface;
class UStaticMesh;

/** Ordu isareti: ulke renkli blok + organizasyon cubugu. Tiklanabilir (ECC_Visibility). */
UCLASS()
class CEPHE1914_API AArmyCounterActor : public AActor
{
	GENERATED_BODY()

public:
	AArmyCounterActor();

	void Init(int32 InArmyIndex, const FLinearColor& NationColor, float Organization);
	void SetOrganization(float Organization);
	int32 GetArmyIndex() const { return ArmyIndex; }

	UPROPERTY(EditAnywhere, Category = "Cephe") TSoftObjectPtr<UStaticMesh> CounterMeshAsset;
	UPROPERTY(EditAnywhere, Category = "Cephe") TSoftObjectPtr<UMaterialInterface> ColorMaterialAsset;
	UPROPERTY(EditAnywhere, Category = "Cephe") FName ColorParam = TEXT("NationColor");
	/** SM_ArmyCounter'da bayrak/sembol ust yuz malzeme slotu. */
	UPROPERTY(EditAnywhere, Category = "Cephe") int32 TintSlot = 1;
	/** Blok mesh'i varsayilan kup ise boyutlari (cm); gercek SM_ArmyCounter icin bu degerler yalnizca cubuk konumunu belirler. */
	UPROPERTY(EditAnywhere, Category = "Cephe") FVector BlockSize = FVector(300.f, 200.f, 80.f);
	UPROPERTY(EditAnywhere, Category = "Cephe") float BarMaxLength = 300.f;
	UPROPERTY(EditAnywhere, Category = "Cephe") float BarThickness = 40.f;

private:
	UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Block;
	UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Bar;
	UPROPERTY() TObjectPtr<UMaterialInstanceDynamic> BarMID;
	int32 ArmyIndex = -1;
	bool bUsingFallbackMesh = false;
};
