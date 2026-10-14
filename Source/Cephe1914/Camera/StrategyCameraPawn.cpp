#include "Camera/StrategyCameraPawn.h"
#include "Core/CepheTypes.h"
#include "Game/CephePlayerController.h"
#include "Game/CepheInput.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Components/SceneComponent.h"
#include "EnhancedInputComponent.h"
#include "InputActionValue.h"

AStrategyCameraPawn::AStrategyCameraPawn()
{
	PrimaryActorTick.bCanEverTick = true;

	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);

	Arm = CreateDefaultSubobject<USpringArmComponent>(TEXT("Arm"));
	Arm->SetupAttachment(Root);
	Arm->bDoCollisionTest = false;
	Arm->bUsePawnControlRotation = false;
	Arm->bInheritPitch = false;
	Arm->bInheritYaw = false;
	Arm->bInheritRoll = false;
	Arm->TargetArmLength = ArmLengthFar;
	Arm->SetRelativeRotation(FRotator(PitchFar, 0.f, 0.f));

	Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
	Camera->SetupAttachment(Arm, USpringArmComponent::SocketName);
	Camera->SetFieldOfView(FovFar);

	AutoPossessPlayer = EAutoReceiveInput::Disabled;
}

void AStrategyCameraPawn::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	UEnhancedInputComponent* EIC = Cast<UEnhancedInputComponent>(PlayerInputComponent);
	ACephePlayerController* PC = Cast<ACephePlayerController>(GetController());
	if (!EIC || !PC) return;
	UCepheInputConfig* In = PC->GetInputConfig();

	EIC->BindAction(In->Move, ETriggerEvent::Triggered, this, &AStrategyCameraPawn::OnMove);
	EIC->BindAction(In->Zoom, ETriggerEvent::Triggered, this, &AStrategyCameraPawn::OnZoom);
	EIC->BindAction(In->Rotate, ETriggerEvent::Triggered, this, &AStrategyCameraPawn::OnRotate);
}

void AStrategyCameraPawn::OnMove(const FInputActionValue& Value)
{
	MoveInput = Value.Get<FVector2D>();
}

void AStrategyCameraPawn::OnZoom(const FInputActionValue& Value)
{
	const float V = Value.Get<float>();
	if (V > 0.f) ZoomLevel = FMath::Min(ZoomLevel + 1, 2);
	else if (V < 0.f) ZoomLevel = FMath::Max(ZoomLevel - 1, 0);
}

void AStrategyCameraPawn::OnRotate(const FInputActionValue& Value)
{
	RotateInput = Value.Get<float>();
}

void AStrategyCameraPawn::FocusOn(const FVector& WorldPos)
{
	SetActorLocation(FVector(WorldPos.X, WorldPos.Y, 0.0));
}

void AStrategyCameraPawn::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	// Yakinlastirma: seviye -> alfa, yumusak gecis; egim, kol uzunlugu ve FOV alfa ile degisir.
	const float TargetAlpha = ZoomLevel / 2.f;
	ZoomAlpha = FMath::FInterpTo(ZoomAlpha, TargetAlpha, DeltaSeconds, ZoomInterpSpeed);
	Arm->TargetArmLength = FMath::Lerp(ArmLengthFar, ArmLengthNear, ZoomAlpha);

	Yaw += RotateInput * RotateSpeedDeg * DeltaSeconds;
	RotateInput = 0.f;
	Arm->SetRelativeRotation(FRotator(FMath::Lerp(PitchFar, PitchNear, ZoomAlpha), Yaw, 0.f));
	Camera->SetFieldOfView(FMath::Lerp(FovFar, FovNear, ZoomAlpha));

	// Kenar kaydirma (arayuz ustundeyken kapali).
	FVector2D Input = MoveInput;
	MoveInput = FVector2D::ZeroVector;
	if (bEdgeScroll)
	{
		if (ACephePlayerController* PC = Cast<ACephePlayerController>(GetController()))
		{
			float MX = 0.f, MY = 0.f;
			int32 VX = 0, VY = 0;
			PC->GetViewportSize(VX, VY);
			if (VX > 0 && VY > 0 && PC->GetMousePosition(MX, MY) && !PC->IsPointerOverUI())
			{
				if (MX <= EdgeScrollMarginPx) Input.X -= 1.f;
				else if (MX >= VX - EdgeScrollMarginPx) Input.X += 1.f;
				if (MY <= EdgeScrollMarginPx) Input.Y += 1.f;
				else if (MY >= VY - EdgeScrollMarginPx) Input.Y -= 1.f;
			}
		}
	}
	Input = Input.ClampAxes(-1.0, 1.0);

	if (!Input.IsNearlyZero())
	{
		const FRotator YawRot(0.f, Yaw, 0.f);
		const FVector Fwd = FRotationMatrix(YawRot).GetUnitAxis(EAxis::X);
		const FVector Right = FRotationMatrix(YawRot).GetUnitAxis(EAxis::Y);
		const float Speed = FMath::Lerp(PanSpeedFar, PanSpeedNear, ZoomAlpha);
		const FVector Delta = (Fwd * Input.Y + Right * Input.X) * Speed * DeltaSeconds;
		SetActorLocation(GetActorLocation() + Delta);
	}

	// Harita sinirina kenetle.
	FVector P = GetActorLocation();
	const double HX = CepheMap::WidthCm * 0.5 + BoundsMarginCm;
	const double HY = CepheMap::HeightCm * 0.5 + BoundsMarginCm;
	P.X = FMath::Clamp(P.X, -HX, HX);
	P.Y = FMath::Clamp(P.Y, -HY, HY);
	P.Z = 0.0;
	SetActorLocation(P);
}
