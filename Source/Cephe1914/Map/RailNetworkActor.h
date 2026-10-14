#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RailNetworkActor.generated.h"

class UStaticMesh;
class UMaterialInterface;

/** rails.json: spline + SplineMesh demiryolu seritleri. */
UCLASS()
class CEPHE1914_API ARailNetworkActor : public AActor
{
	GENERATED_BODY()

public:
	ARailNetworkActor();
	virtual void BeginPlay() override;

	UPROPERTY(EditAnywhere, Category = "Cephe") TSoftObjectPtr<UStaticMesh> StripMeshAsset;
	UPROPERTY(EditAnywhere, Category = "Cephe") TSoftObjectPtr<UMaterialInterface> StripMaterialAsset;
	UPROPERTY(EditAnywhere, Category = "Cephe") FName ColorParam = TEXT("Color");
	UPROPERTY(EditAnywhere, Category = "Cephe") FLinearColor RailColor = FLinearColor(0.12f, 0.10f, 0.09f, 1.f);
	UPROPERTY(EditAnywhere, Category = "Cephe") float ZOffset = 20.f;
	UPROPERTY(EditAnywhere, Category = "Cephe") float MinStepCm = 250.f;
	UPROPERTY(EditAnywhere, Category = "Cephe") float WidthScale = 1.f;
};
