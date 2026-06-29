package com.onip.attendance.storage;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import java.util.ArrayList;
import java.util.List;

/**
 * File d'attente locale des pointages en attente de synchronisation RH.
 */
public class OfflinePunchQueue extends SQLiteOpenHelper {

    public static class PendingPunch {
        public long id;
        public int employeeId;
        public String date;
        public String time;
    }

    private static final String DB_NAME = "presence_offline.db";
    private static final int DB_VERSION = 1;

    public OfflinePunchQueue(Context context) {
        super(context, DB_NAME, null, DB_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL(
                "CREATE TABLE pending_punches (" +
                        "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
                        "employee_id INTEGER NOT NULL, " +
                        "punch_date TEXT NOT NULL, " +
                        "punch_time TEXT NOT NULL, " +
                        "created_at INTEGER NOT NULL" +
                        ")"
        );
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS pending_punches");
        onCreate(db);
    }

    public long enqueue(int employeeId, String date, String time) {
        ContentValues values = new ContentValues();
        values.put("employee_id", employeeId);
        values.put("punch_date", date);
        values.put("punch_time", time);
        values.put("created_at", System.currentTimeMillis());
        return getWritableDatabase().insert("pending_punches", null, values);
    }

    public List<PendingPunch> listAll() {
        List<PendingPunch> rows = new ArrayList<>();
        SQLiteDatabase db = getReadableDatabase();
        Cursor cursor = db.query("pending_punches", null, null, null, null, null, "id ASC");
        try {
            while (cursor.moveToNext()) {
                PendingPunch punch = new PendingPunch();
                punch.id = cursor.getLong(cursor.getColumnIndexOrThrow("id"));
                punch.employeeId = cursor.getInt(cursor.getColumnIndexOrThrow("employee_id"));
                punch.date = cursor.getString(cursor.getColumnIndexOrThrow("punch_date"));
                punch.time = cursor.getString(cursor.getColumnIndexOrThrow("punch_time"));
                rows.add(punch);
            }
        } finally {
            cursor.close();
        }
        return rows;
    }

    public void remove(long id) {
        getWritableDatabase().delete("pending_punches", "id = ?", new String[]{String.valueOf(id)});
    }

    public int count() {
        SQLiteDatabase db = getReadableDatabase();
        Cursor cursor = db.rawQuery("SELECT COUNT(*) FROM pending_punches", null);
        try {
            if (cursor.moveToFirst()) {
                return cursor.getInt(0);
            }
        } finally {
            cursor.close();
        }
        return 0;
    }
}
