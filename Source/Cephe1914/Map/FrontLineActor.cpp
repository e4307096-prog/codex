#include "Map/FrontLineActor.h"
#include "Map/ProvinceMapSubsystem.h"
#include "Cephe1914.h"
#include "Core/CepheUtil.h"
#include "Components/SceneComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"

AFrontLineActor::AFrontLineActor()
{
	PrimaryActorTick.bCanEverTick = false;
	SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
	StripMeshAsset = TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Map/Meshes/SM_TrenchStrip.SM_TrenchStrip")));
	StripMaterialAsset = TSoftObjectPtr<UMaterialInterface>(FSoftObjectPath(TEXT("/Game/Map/M_Strip.M_Strip")));
}

void AFrontLineActor::BeginPlay()
{
	Super::BeginPlay();
	UProvinceMapSubsystem* Map = GetWorld()->GetSubsystem<UProvinceMapSubsystem>();
	if (!Map) return;
	Map->EnsureLoaded();

	UStaticMesh* Mesh = StripMeshAsset.LoadSynchronous();
	if (!Mesh)
	{
		UE_LOG(LogCephe, Warning, TEXT("SM_TrenchStrip yok, cephe cizilmedi"));
		return;
	}
	UMaterialInterface* Base = StripMaterialAsset.LoadSynchronous();
	if (!Base) Base = Mesh->GetMaterial(0);

	const FLinearColor Light(0.62f, 0.52f, 0.34f), Dark(0.20f, 0.11f, 0.07f);
	for (const FFrontLine& F : Map->GetFronts())
	{
		if (F.Points.Num() < 2) continue;
		TArray<FVector> Pts;
		Pts.Reserve(F.Points.Num());
		for (const FVector2D& UV : F.Points)
		{
			Pts.Add(CepheMap::UVToWorld(UV, ZOffset));
		}
		UMaterialInterface* Mat = nullptr;
		if (Base)
		{
			UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(Base, this);
			MID->SetVectorParameterValue(ColorParam, FMath::Lerp(Light, Dark, F.Trench / 5.f));
			Mat = MID;
		}
		const float Width = 0.5f + 0.3f * F.Trench; // siper seviyesi 0-5 -> 0.5..2.0 kati genislik
		CepheUtil::BuildSplineStrip(this, Pts, Mesh, Mat, Width, MinStepCm);
	}
}
