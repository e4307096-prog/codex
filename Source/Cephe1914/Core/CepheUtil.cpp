#include "Core/CepheUtil.h"
#include "Cephe1914.h"
#include "GameFramework/Actor.h"
#include "Components/MeshComponent.h"
#include "Components/SplineComponent.h"
#include "Components/SplineMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"

UMaterialInstanceDynamic* CepheUtil::TintSlot(UMeshComponent* Comp, int32 Slot, UMaterialInterface* Override,
                                              FName Param, const FLinearColor& Color)
{
	if (!Comp) return nullptr;
	UMaterialInterface* Base = Override ? Override : Comp->GetMaterial(Slot);
	if (!Base) return nullptr;
	UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(Base, Comp);
	if (!MID) return nullptr;
	MID->SetVectorParameterValue(Param, Color);
	Comp->SetMaterial(Slot, MID);
	return MID;
}

void CepheUtil::BuildSplineStrip(AActor* Owner, const TArray<FVector>& WorldPts, UStaticMesh* Mesh,
                                 UMaterialInterface* Material, float WidthScale, float MinStepCm)
{
	if (!Owner || !Mesh || WorldPts.Num() < 2) return;

	// Cok sik noktalari ele (son nokta daima kalir).
	TArray<FVector> Pts;
	Pts.Add(WorldPts[0]);
	for (int32 i = 1; i < WorldPts.Num(); ++i)
	{
		const bool bLast = (i == WorldPts.Num() - 1);
		if (bLast || FVector::Dist(WorldPts[i], Pts.Last()) >= MinStepCm)
		{
			Pts.Add(WorldPts[i]);
		}
	}
	if (Pts.Num() < 2) return;

	USplineComponent* Spline = NewObject<USplineComponent>(Owner);
	Spline->SetupAttachment(Owner->GetRootComponent());
	Spline->RegisterComponent();
	Spline->SetSplinePoints(Pts, ESplineCoordinateSpace::World, true);

	const int32 Num = Spline->GetNumberOfSplinePoints();
	for (int32 i = 0; i < Num - 1; ++i)
	{
		const FVector StartPos = Spline->GetLocationAtSplinePoint(i, ESplineCoordinateSpace::Local);
		const FVector StartTan = Spline->GetLeaveTangentAtSplinePoint(i, ESplineCoordinateSpace::Local);
		const FVector EndPos = Spline->GetLocationAtSplinePoint(i + 1, ESplineCoordinateSpace::Local);
		const FVector EndTan = Spline->GetArriveTangentAtSplinePoint(i + 1, ESplineCoordinateSpace::Local);

		USplineMeshComponent* Seg = NewObject<USplineMeshComponent>(Owner);
		Seg->SetStaticMesh(Mesh);
		Seg->SetForwardAxis(ESplineMeshAxis::X, false);
		Seg->SetStartAndEnd(StartPos, StartTan, EndPos, EndTan, false);
		Seg->SetStartScale(FVector2D(WidthScale, WidthScale), false);
		Seg->SetEndScale(FVector2D(WidthScale, WidthScale), false);
		Seg->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Seg->SetupAttachment(Owner->GetRootComponent());
		if (Material)
		{
			Seg->SetMaterial(0, Material);
		}
		Seg->RegisterComponent();
		Seg->UpdateMesh();
	}
}
