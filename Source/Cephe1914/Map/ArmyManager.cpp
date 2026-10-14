#include "Map/ArmyManager.h"
#include "Map/ArmyCounterActor.h"
#include "Map/ProvinceMapSubsystem.h"
#include "Cephe1914.h"
#include "Components/SceneComponent.h"
#include "Engine/World.h"

AArmyManager::AArmyManager()
{
	PrimaryActorTick.bCanEverTick = false;
	SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
}

void AArmyManager::BeginPlay()
{
	Super::BeginPlay();
	UProvinceMapSubsystem* Map = GetWorld()->GetSubsystem<UProvinceMapSubsystem>();
	if (!Map) return;
	Map->EnsureLoaded();

	TMap<int32, int32> PerProvince;
	const TArray<FArmyRecord>& Armies = Map->GetArmies();
	for (int32 i = 0; i < Armies.Num(); ++i)
	{
		const FArmyRecord& A = Armies[i];
		const FProvinceRow* P = Map->FindProvince(A.Province);
		if (!P)
		{
			UE_LOG(LogCephe, Warning, TEXT("Ordu '%s': bolge %d bulunamadi"), *A.Name, A.Province);
			continue;
		}
		const int32 Slot = PerProvince.FindOrAdd(A.Province)++;
		FVector Pos = CepheMap::UVToWorld(FVector2D(P->CentroidU, P->CentroidV), ZOffset);
		Pos.X += Slot * StackSpacing;

		FActorSpawnParameters Params;
		Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		AArmyCounterActor* C = GetWorld()->SpawnActor<AArmyCounterActor>(Pos, FRotator::ZeroRotator, Params);
		if (!C) continue;
		C->SetActorScale3D(FVector(CounterScale));
		C->Init(i, Map->GetNationColor(A.Nation), A.Organization);
		Counters.Add(C);
	}
}
