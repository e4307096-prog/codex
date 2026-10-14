#include "Game/CepheClock.h"
#include "Engine/World.h"
#include "Stats/Stats.h"

bool UCepheClock::ShouldCreateSubsystem(UObject* Outer) const
{
	const UWorld* W = Cast<UWorld>(Outer);
	return W && W->IsGameWorld() && Super::ShouldCreateSubsystem(Outer);
}

TStatId UCepheClock::GetStatId() const
{
	RETURN_QUICK_DECLARE_CYCLE_STAT(UCepheClock, STATGROUP_Tickables);
}

void UCepheClock::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	if (Speed <= 0) return;

	// Hiz 1..4: bir oyun saati icin gercek saniye.
	static const float SecondsPerHour[5] = { 0.f, 1.0f, 0.5f, 0.2f, 0.05f };
	Accumulator += DeltaTime;
	const float Step = SecondsPerHour[FMath::Clamp(Speed, 1, 4)];
	int32 Guard = 24; // kare basina en fazla 24 saat
	while (Accumulator >= Step && Guard-- > 0)
	{
		Accumulator -= Step;
		const int32 OldDay = Current.GetDay();
		Current += FTimespan::FromHours(1.0);
		OnHourTick.Broadcast(Current);
		if (Current.GetDay() != OldDay)
		{
			OnDayChanged.Broadcast(Current);
		}
	}
	if (Guard <= 0) Accumulator = 0.f;
}

void UCepheClock::SetSpeed(int32 NewSpeed)
{
	NewSpeed = FMath::Clamp(NewSpeed, 0, 4);
	if (NewSpeed == Speed) return;
	if (NewSpeed > 0) LastSpeed = NewSpeed;
	Speed = NewSpeed;
	OnSpeedChanged.Broadcast(Speed);
}

void UCepheClock::TogglePause()
{
	SetSpeed(IsPaused() ? LastSpeed : 0);
}
