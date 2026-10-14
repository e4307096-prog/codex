#pragma once

#include "CoreMinimal.h"

/** fronts.json: { "a": idA, "b": idB, "trench": 0-5, "points": [[u,v],...] } */
struct FFrontLine
{
	int32 A = 0;
	int32 B = 0;
	int32 Trench = 0;
	TArray<FVector2D> Points;
};

/** rails.json: { "name": "...", "points": [[u,v],...] } */
struct FRailLine
{
	FString Name;
	TArray<FVector2D> Points;
};

/** armies.json: { "name", "nation", "province", "divisions", "organization" } */
struct FArmyRecord
{
	FString Name;
	FString Nation;
	int32 Province = 0;
	int32 Divisions = 1;
	float Organization = 1.f;
};

/** adjacency.json: [idA, idB, borderPixels] */
struct FAdjacencyEdge
{
	int32 A = 0;
	int32 B = 0;
	int32 BorderPixels = 0;
};

/** Content/Map/Raw altindaki ham dosyalari okuyan yukleyiciler. */
namespace CepheData
{
	CEPHE1914_API FString RawPath(const TCHAR* FileName);
	CEPHE1914_API bool LoadFronts(TArray<FFrontLine>& Out);
	CEPHE1914_API bool LoadRails(TArray<FRailLine>& Out);
	CEPHE1914_API bool LoadArmies(TArray<FArmyRecord>& Out);
	CEPHE1914_API bool LoadAdjacency(TArray<FAdjacencyEdge>& Out);
}
