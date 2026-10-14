#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Core/CepheTypes.h"
#include "ProvinceMapActor.generated.h"

class UStaticMeshComponent;
class UStaticMesh;
class UMaterialInterface;
class UMaterialInstanceDynamic;
class UTexture;
class UProvinceMapSubsystem;

/** Harita levhasi: mesh, dinamik malzeme, imlec altindaki bolge. */
UCLASS()
class CEPHE1914_API AProvinceMapActor : public AActor
{
	GENERATED_BODY()

public:
	AProvinceMapActor();

	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
	virtual void Tick(float DeltaSeconds) override;

	UPROPERTY(EditAnywhere, Category = "Cephe") TSoftObjectPtr<UStaticMesh> BoardMeshAsset;
	UPROPERTY(EditAnywhere, Category = "Cephe") TSoftObjectPtr<UMaterialInterface> MapMaterialAsset;
	UPROPERTY(EditAnywhere, Category = "Cephe") TSoftObjectPtr<UTexture> IdTextureAsset;
	UPROPERTY(EditAnywhere, Category = "Cephe") TSoftObjectPtr<UTexture> HeightTextureAsset;
	UPROPERTY(EditAnywhere, Category = "Cephe") TSoftObjectPtr<UTexture> PaperTextureAsset;

	/** Imlec isininin kesistigi duzlemin yuksekligi (cm). */
	UPROPERTY(EditAnywhere, Category = "Cephe") float HoverPlaneZ = 100.f;

	UPROPERTY(EditAnywhere, Category = "Cephe") FLinearColor BorderColor = FLinearColor(0.10f, 0.08f, 0.06f, 1.f);
	UPROPERTY(EditAnywhere, Category = "Cephe") FLinearColor NationBorderColor = FLinearColor(0.04f, 0.03f, 0.02f, 1.f);
	UPROPERTY(EditAnywhere, Category = "Cephe") FLinearColor SeaColor = FLinearColor(0.10f, 0.20f, 0.26f, 1.f);
	UPROPERTY(EditAnywhere, Category = "Cephe") float HillshadeStrength = 0.6f;

private:
	void ApplyMaterialParams();
	void HandleMapMode(EMapMode Mode);

	UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> BoardMesh;
	UPROPERTY() TObjectPtr<UMaterialInstanceDynamic> Material;
	TWeakObjectPtr<UProvinceMapSubsystem> Map;
};
