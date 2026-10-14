#include "Core/CepheData.h"
#include "Cephe1914.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Dom/JsonObject.h"
#include "Dom/JsonValue.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

FString CepheData::RawPath(const TCHAR* FileName)
{
	return FPaths::Combine(FPaths::ProjectContentDir(), TEXT("Map/Raw"), FileName);
}

namespace
{
	bool ReadJsonArray(const TCHAR* FileName, TArray<TSharedPtr<FJsonValue>>& Out)
	{
		FString Text;
		const FString Path = CepheData::RawPath(FileName);
		if (!FFileHelper::LoadFileToString(Text, *Path))
		{
			UE_LOG(LogCephe, Warning, TEXT("JSON okunamadi: %s"), *Path);
			return false;
		}
		TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
		if (!FJsonSerializer::Deserialize(Reader, Out))
		{
			UE_LOG(LogCephe, Warning, TEXT("JSON ayristirilamadi: %s"), *Path);
			return false;
		}
		return true;
	}

	void ReadPoints(const TSharedPtr<FJsonObject>& Obj, TArray<FVector2D>& Pts)
	{
		const TArray<TSharedPtr<FJsonValue>>* Arr = nullptr;
		if (!Obj->TryGetArrayField(TEXT("points"), Arr) || !Arr)
		{
			return;
		}
		for (const TSharedPtr<FJsonValue>& V : *Arr)
		{
			const TArray<TSharedPtr<FJsonValue>>* P = nullptr;
			if (V.IsValid() && V->TryGetArray(P) && P && P->Num() >= 2)
			{
				Pts.Add(FVector2D((*P)[0]->AsNumber(), (*P)[1]->AsNumber()));
			}
		}
	}
}

bool CepheData::LoadFronts(TArray<FFrontLine>& Out)
{
	TArray<TSharedPtr<FJsonValue>> Arr;
	if (!ReadJsonArray(TEXT("fronts.json"), Arr)) return false;
	for (const TSharedPtr<FJsonValue>& V : Arr)
	{
		const TSharedPtr<FJsonObject>* O = nullptr;
		if (!V.IsValid() || !V->TryGetObject(O) || !O) continue;
		FFrontLine L;
		double D = 0;
		if ((*O)->TryGetNumberField(TEXT("a"), D)) L.A = static_cast<int32>(D);
		if ((*O)->TryGetNumberField(TEXT("b"), D)) L.B = static_cast<int32>(D);
		if ((*O)->TryGetNumberField(TEXT("trench"), D)) L.Trench = FMath::Clamp(static_cast<int32>(D), 0, 5);
		ReadPoints(*O, L.Points);
		Out.Add(MoveTemp(L));
	}
	return true;
}

bool CepheData::LoadRails(TArray<FRailLine>& Out)
{
	TArray<TSharedPtr<FJsonValue>> Arr;
	if (!ReadJsonArray(TEXT("rails.json"), Arr)) return false;
	for (const TSharedPtr<FJsonValue>& V : Arr)
	{
		const TSharedPtr<FJsonObject>* O = nullptr;
		if (!V.IsValid() || !V->TryGetObject(O) || !O) continue;
		FRailLine L;
		(*O)->TryGetStringField(TEXT("name"), L.Name);
		ReadPoints(*O, L.Points);
		Out.Add(MoveTemp(L));
	}
	return true;
}

bool CepheData::LoadArmies(TArray<FArmyRecord>& Out)
{
	TArray<TSharedPtr<FJsonValue>> Arr;
	if (!ReadJsonArray(TEXT("armies.json"), Arr)) return false;
	for (const TSharedPtr<FJsonValue>& V : Arr)
	{
		const TSharedPtr<FJsonObject>* O = nullptr;
		if (!V.IsValid() || !V->TryGetObject(O) || !O) continue;
		FArmyRecord R;
		double D = 0;
		(*O)->TryGetStringField(TEXT("name"), R.Name);
		(*O)->TryGetStringField(TEXT("nation"), R.Nation);
		if ((*O)->TryGetNumberField(TEXT("province"), D)) R.Province = static_cast<int32>(D);
		if ((*O)->TryGetNumberField(TEXT("divisions"), D)) R.Divisions = FMath::Max(1, static_cast<int32>(D));
		if ((*O)->TryGetNumberField(TEXT("organization"), D)) R.Organization = FMath::Clamp(static_cast<float>(D), 0.f, 1.f);
		Out.Add(MoveTemp(R));
	}
	return true;
}

bool CepheData::LoadAdjacency(TArray<FAdjacencyEdge>& Out)
{
	TArray<TSharedPtr<FJsonValue>> Arr;
	if (!ReadJsonArray(TEXT("adjacency.json"), Arr)) return false;
	for (const TSharedPtr<FJsonValue>& V : Arr)
	{
		const TArray<TSharedPtr<FJsonValue>>* P = nullptr;
		if (!V.IsValid() || !V->TryGetArray(P) || !P || P->Num() < 2) continue;
		FAdjacencyEdge E;
		E.A = static_cast<int32>((*P)[0]->AsNumber());
		E.B = static_cast<int32>((*P)[1]->AsNumber());
		if (P->Num() >= 3) E.BorderPixels = static_cast<int32>((*P)[2]->AsNumber());
		Out.Add(E);
	}
	return true;
}
