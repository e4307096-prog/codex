#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FrontLineActor.generated.h"

class UStaticMesh;
class UMaterialInterface;

/** fronts.json: spline + SplineMesh siper seritleri; genislik ve renk siper seviyesine gore. */
UCLASS()
class CEPHE1914_API AFrontLineActor : public AActor
{
	GENERATED_BODY()

public:
	AFrontLineActor();
	virtual void BeginPlay() override;

	UPROPERTY(EditAnywhere, Category = "Cephe") TSoftObjectPtr<UStaticMesh> StripMeshAsset;
	/** Ters verilirse (yoksa mesh'in kendi malzemesi) "Color" vektor parametresi boyanir. */
	UPROPERTY(EditAnywhere, Category = "Cephe") TSoftObjectPtr<UMaterialInterface> StripMaterialAsset;
	UPROPERTY(EditAnywhere, Category = "Cephe") FName ColorParam = TEXT("Color");
	UPROPERTY(EditAnywhere, Category = "Cephe") float ZOffset = 30.f;
	UPROPERTY(EditAnywhere, Category = "Cephe") float MinStepCm = 250.f;
};
