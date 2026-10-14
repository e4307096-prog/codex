#include "Map/ArmyCounterActor.h"
#include "Cephe1914.h"
#include "Core/CepheUtil.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"

AArmyCounterActor::AArmyCounterActor()
{
	PrimaryActorTick.bCanEverTick = false;

	Block = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Block"));
	SetRootComponent(Block);
	Block->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Block->SetCollisionResponseToAllChannels(ECR_Ignore);
	Block->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);

	Bar = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Bar"));
	Bar->SetupAttachment(Block);
	Bar->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	CounterMeshAsset = TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Map/Meshes/SM_ArmyCounter.SM_ArmyCounter")));
	ColorMaterialAsset = TSoftObjectPtr<UMaterialInterface>(FSoftObjectPath(TEXT("/Game/Map/M_CounterColor.M_CounterColor")));
}

void AArmyCounterActor::Init(int32 InArmyIndex, const FLinearColor& NationColor, float Organization)
{
	ArmyIndex = InArmyIndex;

	UStaticMesh* Cube = CepheUtil::LoadQuiet<UStaticMesh>(TEXT("/Engine/BasicShapes/Cube.Cube"));
	UStaticMesh* Mesh = CounterMeshAsset.LoadSynchronous();
	if (!Mesh)
	{
		bUsingFallbackMesh = true;
		Mesh = Cube;
		Block->SetRelativeScale3D(BlockSize / 100.0);
	}
	Block->SetStaticMesh(Mesh);

	UMaterialInterface* ColorMat = ColorMaterialAsset.LoadSynchronous();
	const int32 Slot = Block->GetNumMaterials() > TintSlot ? TintSlot : 0;
	CepheUtil::TintSlot(Block, Slot, ColorMat, ColorParam, NationColor);

	// Cubuk: 100 cm'lik kup, blok uzerinde one dogru; olcek blok olceginin tersiyle duzeltilir.
	Bar->SetStaticMesh(Cube);
	const FVector Inv = bUsingFallbackMesh ? FVector(100.0) / BlockSize : FVector::OneVector;
	Bar->SetRelativeScale3D(Inv * FVector(1.0, 1.0, 1.0) * 0.01 * FVector(BarMaxLength, BarThickness, BarThickness));
	SetOrganization(Organization);
}

void AArmyCounterActor::SetOrganization(float Organization)
{
	Organization = FMath::Clamp(Organization, 0.02f, 1.f);
	const FVector Inv = bUsingFallbackMesh ? FVector(100.0) / BlockSize : FVector::OneVector;
	const double Len = BarMaxLength * Organization;
	Bar->SetRelativeScale3D(Inv * 0.01 * FVector(Len, BarThickness, BarThickness));
	// Sola yasli: blok onunde (-Y yonu), uzunluk X boyunca.
	const FVector Local(-BarMaxLength * 0.5 + Len * 0.5, -(BlockSize.Y * 0.5 + BarThickness), BarThickness * 0.5);
	Bar->SetRelativeLocation(bUsingFallbackMesh ? Local * Inv : Local);

	const FLinearColor C = FMath::Lerp(FLinearColor(0.70f, 0.12f, 0.08f), FLinearColor(0.20f, 0.55f, 0.20f), Organization);
	if (!BarMID)
	{
		BarMID = CepheUtil::TintSlot(Bar, 0, nullptr, ColorParam, C);
	}
	else
	{
		BarMID->SetVectorParameterValue(ColorParam, C);
	}
}
