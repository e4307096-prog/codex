#include "Game/CephePlayerController.h"
#include "Game/CepheInput.h"
#include "Game/CepheClock.h"
#include "Game/CepheHUD.h"
#include "Map/ProvinceMapSubsystem.h"
#include "Map/ArmyCounterActor.h"
#include "Core/CepheTypes.h"
#include "Engine/World.h"
#include "Engine/LocalPlayer.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputMappingContext.h"

ACephePlayerController::ACephePlayerController()
{
	bShowMouseCursor = true;
	DefaultMouseCursor = EMouseCursor::Default;
}

UCepheInputConfig* ACephePlayerController::GetInputConfig()
{
	if (!InputConfig)
	{
		InputConfig = NewObject<UCepheInputConfig>(this);
		InputConfig->Build();
	}
	return InputConfig;
}

void ACephePlayerController::BeginPlay()
{
	Super::BeginPlay();

	if (ULocalPlayer* LP = GetLocalPlayer())
	{
		if (UEnhancedInputLocalPlayerSubsystem* Sub = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(LP))
		{
			Sub->AddMappingContext(GetInputConfig()->Context, 0);
		}
	}

	FInputModeGameAndUI Mode;
	Mode.SetHideCursorDuringCapture(false);
	Mode.SetLockMouseToViewportBehavior(EMouseLockMode::LockAlways);
	SetInputMode(Mode);
	bShowMouseCursor = true;
}

void ACephePlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();

	UEnhancedInputComponent* EIC = Cast<UEnhancedInputComponent>(InputComponent);
	if (!EIC) return;
	UCepheInputConfig* In = GetInputConfig();

	EIC->BindAction(In->Click, ETriggerEvent::Started, this, &ACephePlayerController::OnClick);
	EIC->BindAction(In->Pause, ETriggerEvent::Started, this, &ACephePlayerController::OnPause);
	EIC->BindAction(In->SpeedUp, ETriggerEvent::Started, this, &ACephePlayerController::OnSpeedUp);
	EIC->BindAction(In->SpeedDown, ETriggerEvent::Started, this, &ACephePlayerController::OnSpeedDown);
	EIC->BindAction(In->Mode1, ETriggerEvent::Started, this, &ACephePlayerController::OnMode1);
	EIC->BindAction(In->Mode2, ETriggerEvent::Started, this, &ACephePlayerController::OnMode2);
	EIC->BindAction(In->Mode3, ETriggerEvent::Started, this, &ACephePlayerController::OnMode3);
	EIC->BindAction(In->Mode4, ETriggerEvent::Started, this, &ACephePlayerController::OnMode4);
	EIC->BindAction(In->Menu1, ETriggerEvent::Started, this, &ACephePlayerController::OnMenu1);
	EIC->BindAction(In->Menu2, ETriggerEvent::Started, this, &ACephePlayerController::OnMenu2);
	EIC->BindAction(In->Menu3, ETriggerEvent::Started, this, &ACephePlayerController::OnMenu3);
	EIC->BindAction(In->Menu4, ETriggerEvent::Started, this, &ACephePlayerController::OnMenu4);
	EIC->BindAction(In->Menu5, ETriggerEvent::Started, this, &ACephePlayerController::OnMenu5);
	EIC->BindAction(In->Menu6, ETriggerEvent::Started, this, &ACephePlayerController::OnMenu6);
}

bool ACephePlayerController::IsPointerOverUI() const
{
	const ACepheHUD* H = Cast<ACepheHUD>(GetHUD());
	return H && H->IsPointerOverUI();
}

void ACephePlayerController::OnClick()
{
	if (IsPointerOverUI()) return;
	UProvinceMapSubsystem* Map = GetWorld()->GetSubsystem<UProvinceMapSubsystem>();
	if (!Map) return;

	FHitResult Hit;
	if (GetHitResultUnderCursor(ECC_Visibility, false, Hit))
	{
		if (const AArmyCounterActor* Army = Cast<AArmyCounterActor>(Hit.GetActor()))
		{
			Map->SelectArmy(Army->GetArmyIndex());
			return;
		}
	}
	Map->SelectProvince(Map->GetHoveredProvince());
}

void ACephePlayerController::SetMode(int32 Index)
{
	if (UProvinceMapSubsystem* Map = GetWorld()->GetSubsystem<UProvinceMapSubsystem>())
	{
		Map->SetMapMode(static_cast<EMapMode>(FMath::Clamp(Index, 0, 3)));
	}
}

void ACephePlayerController::OnPause()
{
	if (UCepheClock* C = GetWorld()->GetSubsystem<UCepheClock>()) C->TogglePause();
}

void ACephePlayerController::OnSpeedUp()
{
	if (UCepheClock* C = GetWorld()->GetSubsystem<UCepheClock>()) C->IncreaseSpeed();
}

void ACephePlayerController::OnSpeedDown()
{
	if (UCepheClock* C = GetWorld()->GetSubsystem<UCepheClock>()) C->DecreaseSpeed();
}
