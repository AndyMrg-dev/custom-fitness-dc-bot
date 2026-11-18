using System;
using System.IO;
using Microsoft.Data.Sqlite;

// bot_data.db liegt normalerweise eine Ebene über admin_cli
string dbPath = File.Exists("../bot_data.db") ? "../bot_data.db" : "bot_data.db";

if (!File.Exists(dbPath))
{
    Console.WriteLine($"Datenbank nicht gefunden: {Path.GetFullPath(dbPath)}");
    return;
}

string connStr = $"Data Source={dbPath}";

while (true)
{
    Console.WriteLine("\n=== RONNIE BOT - ADMIN CLI ===");
    Console.WriteLine("1. Alle User anzeigen");
    Console.WriteLine("2. Leaderboard für eine Übung");
    Console.WriteLine("3. PRs und Volumen eines Users");
    Console.WriteLine("4. Verwarnungen anzeigen");
    Console.WriteLine("5. Verwarnungen eines Users löschen");
    Console.WriteLine("0. Beenden");
    Console.Write("\nAuswahl: ");

    string? choice = Console.ReadLine();

    switch (choice)
    {
        case "1":
            ShowUsers(connStr);
            break;
        case "2":
            Console.Write("Übung (z. B. bench press): ");
            string exercise = (Console.ReadLine() ?? "").Trim().ToLower();
            ShowLeaderboard(connStr, exercise);
            break;
        case "3":
            if (ReadId("User-ID: ") is long statsId)
                ShowUserStats(connStr, statsId);
            break;
        case "4":
            ShowWarnings(connStr);
            break;
        case "5":
            if (ReadId("User-ID, dessen Verwarnungen gelöscht werden sollen: ") is long clearId)
                ClearWarnings(connStr, clearId);
            break;
        case "0":
            Console.WriteLine("LIGHTWEIGHT BABY! Bis zum nächsten Mal.");
            return;
        default:
            Console.WriteLine("Ungültige Eingabe.");
            break;
    }
}

// fragt eine ID ab, gibt null zurück wenn keine Zahl eingegeben wurde
static long? ReadId(string prompt)
{
    Console.Write(prompt);
    if (long.TryParse(Console.ReadLine(), out long id))
        return id;

    Console.WriteLine("Ungültige ID.");
    return null;
}

static SqliteCommand CreateCommand(SqliteConnection conn, string sql)
{
    var cmd = conn.CreateCommand();
    cmd.CommandText = sql;
    return cmd;
}

static void ShowUsers(string connStr)
{
    using var conn = new SqliteConnection(connStr);
    conn.Open();

    var cmd = CreateCommand(conn, "SELECT user_id, username, updated_at FROM users ORDER BY updated_at DESC");
    using var reader = cmd.ExecuteReader();

    Console.WriteLine("\n--- Registrierte User ---");
    bool any = false;
    while (reader.Read())
    {
        any = true;
        Console.WriteLine($"ID: {reader.GetInt64(0)} | Name: {reader.GetString(1)} | Zuletzt aktiv: {reader.GetString(2)}");
    }
    if (!any) Console.WriteLine("Keine User vorhanden.");
}

static void ShowLeaderboard(string connStr, string exercise)
{
    using var conn = new SqliteConnection(connStr);
    conn.Open();

    var cmd = CreateCommand(conn, @"
        SELECT u.username, MAX(w.weight_kg), SUM(w.weight_kg * w.reps)
        FROM workouts w
        JOIN users u ON w.user_id = u.user_id
        WHERE w.exercise = $exercise
        GROUP BY u.user_id
        ORDER BY MAX(w.weight_kg) DESC, SUM(w.weight_kg * w.reps) DESC");
    cmd.Parameters.AddWithValue("$exercise", exercise);

    using var reader = cmd.ExecuteReader();
    Console.WriteLine($"\n--- Leaderboard: {exercise} ---");

    int rank = 0;
    while (reader.Read())
    {
        rank++;
        Console.WriteLine($"#{rank} {reader.GetString(0)} -> PR: {reader.GetDouble(1)} kg | Volumen: {reader.GetDouble(2):F0} kg");
    }
    if (rank == 0) Console.WriteLine("Keine Einträge gefunden.");
}

static void ShowUserStats(string connStr, long userId)
{
    using var conn = new SqliteConnection(connStr);
    conn.Open();

    var cmd = CreateCommand(conn, @"
        SELECT exercise, MAX(weight_kg), SUM(weight_kg * reps), COUNT(id)
        FROM workouts
        WHERE user_id = $userId
        GROUP BY exercise
        ORDER BY MAX(weight_kg) DESC");
    cmd.Parameters.AddWithValue("$userId", userId);

    using var reader = cmd.ExecuteReader();
    Console.WriteLine($"\n--- PRs für User-ID {userId} ---");

    bool any = false;
    while (reader.Read())
    {
        any = true;
        Console.WriteLine($"- {reader.GetString(0)}: PR {reader.GetDouble(1)} kg | Sätze: {reader.GetInt32(3)} | Volumen: {reader.GetDouble(2):F0} kg");
    }
    if (!any) Console.WriteLine("Keine Workouts für diese ID vorhanden.");
}

static void ShowWarnings(string connStr)
{
    using var conn = new SqliteConnection(connStr);
    conn.Open();

    var cmd = CreateCommand(conn, @"
        SELECT m.id, u.username, m.target_user_id, m.reason, m.created_at
        FROM moderation_logs m
        JOIN users u ON m.target_user_id = u.user_id
        ORDER BY m.created_at DESC");

    using var reader = cmd.ExecuteReader();
    Console.WriteLine("\n--- Verwarnungen ---");

    bool any = false;
    while (reader.Read())
    {
        any = true;
        Console.WriteLine($"[#{reader.GetInt32(0)}] {reader.GetString(1)} (ID: {reader.GetInt64(2)}) | Grund: {reader.GetString(3)} | Datum: {reader.GetString(4)}");
    }
    if (!any) Console.WriteLine("Keine Verwarnungen vorhanden.");
}

static void ClearWarnings(string connStr, long userId)
{
    using var conn = new SqliteConnection(connStr);
    conn.Open();

    var cmd = CreateCommand(conn, "DELETE FROM moderation_logs WHERE target_user_id = $userId");
    cmd.Parameters.AddWithValue("$userId", userId);

    int deleted = cmd.ExecuteNonQuery();
    Console.WriteLine($"{deleted} Verwarnung(en) für User-ID {userId} gelöscht.");
}