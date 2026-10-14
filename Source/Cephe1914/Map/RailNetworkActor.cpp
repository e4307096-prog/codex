#include "Map/RailNetworkActor.h"
#include "Map/ProvinceMapSubsystem.h"
#include "Cephe1914.h"
#include "Core/CepheUtil.h"
#include "Components/SceneComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"

ARailNetworkActor::ARailNetworkActor()
{
	PrimaryActorTick.bCanEverTick = false;
	SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
	StripMeshAsset = TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Map/Meshes/SM_RailStrip.SM_RailStrip")));
	StripMaterialAsset = TSoftObjectPtr<UMaterialInterface>(FSoftObjectPath(TEXT("/Game/Map/M_Strip.M_Strip")));
}

void ARailNetworkActor::BeginPlay()
{
	Super::BeginPlay();
	UProvinceMapSubsystem* Map = GetWorld()->GetSubsystem<UProvinceMapSubsystem>();
	if (!Map) return;
	Map->EnsureLoaded();

	UStaticMesh* Mesh = StripMeshAsset.LoadSynchronous();
	if (!Mesh)
	{
		UE_LOG(LogCephe, Warning, TEXT("SM_RailStrip yok, demiryolu cizilmedi"));
		return;
	}
	UMaterialInterface* Base = StripMaterialAsset.LoadSynchronous();
	if (!Base) Base = Mesh->GetMaterial(0);
	UMaterialInterface* Mat = nullptr;
	if (Base)
	{
		UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(Base, this);
		MID->SetVectorParameterValue(ColorParam, RailColor);
		Mat = MID;
	}

	for (const FRailLine& R : Map->GetRails())
	{
		if (R.Points.Num() < 2) continue;
		TArray<FVector> Pts;
		Pts.Reserve(R.Points.Num());
		for (const FVector2D& UV : R.Points)
		{
			Pts.Add(CepheMap::UVToWorld(UV, ZOffset));
		}
		CepheUtil::BuildSplineStrip(this, Pts, Mesh, Mat, WidthScale, MinStepCm);
	}
}
