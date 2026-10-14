#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "StrategyCameraPawn.generated.h"

class USpringArmComponent;
class UCameraComponent;
class USceneComponent;
struct FInputActionValue;

/** Strateji kamerasi: WASD/ok, kenar kaydirma, 3 seviye yakinlastirma, Q/E donme, harita siniri. */
UCLASS()
class CEPHE1914_API AStrategyCameraPawn : public APawn
{
	GENERATED_BODY()

public:
	AStrategyCameraPawn();

	virtual void Tick(float DeltaSeconds) override;
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

	void FocusOn(const FVector& WorldPos);

	/** Yakinlastirma seviyeleri: 0 strateji, 1 bolge, 2 taktik. */
	UPROPERTY(EditAnywhere, Category = "Cephe") float ArmLengthFar = 30000.f;
	UPROPERTY(EditAnywhere, Category = "Cephe") float ArmLengthNear = 2500.f;
	UPROPERTY(EditAnywhere, Category = "Cephe") float PitchFar = -70.f;
	UPROPERTY(EditAnywhere, Category = "Cephe") float PitchNear = -38.f;
	UPROPERTY(EditAnywhere, Category = "Cephe") float FovFar = 70.f;
	UPROPERTY(EditAnywhere, Category = "Cephe") float FovNear = 45.f;
	UPROPERTY(EditAnywhere, Category = "Cephe") float PanSpeedFar = 14000.f;
	UPROPERTY(EditAnywhere, Category = "Cephe") float PanSpeedNear = 2500.f;
	UPROPERTY(EditAnywhere, Category = "Cephe") float RotateSpeedDeg = 80.f;
	UPROPERTY(EditAnywhere, Category = "Cephe") float ZoomInterpSpeed = 6.f;
	UPROPERTY(EditAnywhere, Category = "Cephe") float EdgeScrollMarginPx = 8.f;
	UPROPERTY(EditAnywhere, Category = "Cephe") bool bEdgeScroll = true;
	UPROPERTY(EditAnywhere, Category = "Cephe") float BoundsMarginCm = 1500.f;

private:
	void OnMove(const FInputActionValue& Value);
	void OnZoom(const FInputActionValue& Value);
	void OnRotate(const FInputActionValue& Value);

	UPROPERTY(VisibleAnywhere) TObjectPtr<USceneComponent> Root;
	UPROPERTY(VisibleAnywhere) TObjectPtr<USpringArmComponent> Arm;
	UPROPERTY(VisibleAnywhere) TObjectPtr<UCameraComponent> Camera;

	FVector2D MoveInput = FVector2D::ZeroVector;
	float RotateInput = 0.f;
	int32 ZoomLevel = 0;
	float ZoomAlpha = 0.f;
	float Yaw = 0.f;
};
