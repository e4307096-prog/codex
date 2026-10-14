#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "Misc/DateTime.h"
#include "CepheClock.generated.h"

DECLARE_MULTICAST_DELEGATE_OneParam(FOnClockHour, const FDateTime&);
DECLARE_MULTICAST_DELEGATE_OneParam(FOnClockDay, const FDateTime&);
DECLARE_MULTICAST_DELEGATE_OneParam(FOnClockSpeed, int32);

/** Oyun saati: 14 Kasim 1914 00:00'dan baslar; hiz 0 (durdu) - 4; her oyun saatinde tik. */
UCLASS()
class CEPHE1914_API UCepheClock : public UTickableWorldSubsystem
{
	GENERATED_BODY()

public:
	virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
	virtual void Tick(float DeltaTime) override;
	virtual TStatId GetStatId() const override;

	FDateTime GetDate() const { return Current; }
	int32 GetSpeed() const { return Speed; }
	bool IsPaused() const { return Speed == 0; }

	void SetSpeed(int32 NewSpeed);
	void IncreaseSpeed() { SetSpeed(IsPaused() ? LastSpeed : Speed + 1); }
	void DecreaseSpeed() { SetSpeed(Speed - 1); }
	void TogglePause();

	FOnClockHour OnHourTick;
	FOnClockDay OnDayChanged;
	FOnClockSpeed OnSpeedChanged;

private:
	FDateTime Current = FDateTime(1914, 11, 14, 0, 0, 0);
	int32 Speed = 1;
	int32 LastSpeed = 1;
	float Accumulator = 0.f;
};
