package com.onip.attendance.storage;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.util.Base64;
import android.util.Log;
import com.onip.attendance.models.Employee;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Cache local des employés et templates Morpho pour le pointage offline.
 */
public class LocalTemplateStore extends SQLiteOpenHelper {

    private static final String TAG = "LocalTemplateStore";
    private static final String DB_NAME = "presence_templates.db";
    private static final int DB_VERSION = 1;

    public LocalTemplateStore(Context context) {
        super(context, DB_NAME, null, DB_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL(
                "CREATE TABLE employees (" +
                        "id INTEGER PRIMARY KEY, " +
                        "first_name TEXT, " +
                        "last_name TEXT, " +
                        "middle_name TEXT, " +
                        "nin TEXT" +
                        ")"
        );
        db.execSQL(
                "CREATE TABLE templates (" +
                        "employee_id INTEGER NOT NULL, " +
                        "finger_name TEXT NOT NULL, " +
                        "data BLOB NOT NULL, " +
                        "PRIMARY KEY (employee_id, finger_name)" +
                        ")"
        );
        db.execSQL(
                "CREATE TABLE sync_meta (" +
                        "key TEXT PRIMARY KEY, " +
                        "value TEXT" +
                        ")"
        );
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS templates");
        db.execSQL("DROP TABLE IF EXISTS employees");
        db.execSQL("DROP TABLE IF EXISTS sync_meta");
        onCreate(db);
    }

    public void replaceAll(List<Employee> employees, Map<Integer, Map<String, byte[]>> templates) {
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            db.delete("employees", null, null);
            db.delete("templates", null, null);
            if (employees != null) {
                for (Employee employee : employees) {
                    if (employee == null || employee.getId() <= 0) {
                        continue;
                    }
                    ContentValues row = new ContentValues();
                    row.put("id", employee.getId());
                    row.put("first_name", employee.getFirstName());
                    row.put("last_name", employee.getLastName());
                    row.put("middle_name", employee.getMiddleName());
                    row.put("nin", employee.getNin());
                    db.insert("employees", null, row);
                }
            }
            if (templates != null) {
                for (Map.Entry<Integer, Map<String, byte[]>> entry : templates.entrySet()) {
                    int employeeId = entry.getKey();
                    Map<String, byte[]> fingers = entry.getValue();
                    if (fingers == null) {
                        continue;
                    }
                    for (Map.Entry<String, byte[]> finger : fingers.entrySet()) {
                        if (finger.getValue() == null || finger.getValue().length == 0) {
                            continue;
                        }
                        ContentValues tpl = new ContentValues();
                        tpl.put("employee_id", employeeId);
                        tpl.put("finger_name", finger.getKey());
                        tpl.put("data", finger.getValue());
                        db.insert("templates", null, tpl);
                    }
                }
            }
            db.setTransactionSuccessful();
        } finally {
            db.endTransaction();
        }
    }

    public void mergeBundle(List<Employee> employees, Map<Integer, Map<String, byte[]>> templates) {
        if (employees == null || employees.isEmpty()) {
            return;
        }
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            for (Employee employee : employees) {
                ContentValues row = new ContentValues();
                row.put("id", employee.getId());
                row.put("first_name", employee.getFirstName());
                row.put("last_name", employee.getLastName());
                row.put("middle_name", employee.getMiddleName());
                row.put("nin", employee.getNin());
                db.insertWithOnConflict("employees", null, row, SQLiteDatabase.CONFLICT_REPLACE);
            }
            for (Map.Entry<Integer, Map<String, byte[]>> entry : templates.entrySet()) {
                int employeeId = entry.getKey();
                Map<String, byte[]> fingers = entry.getValue();
                if (fingers == null || fingers.isEmpty()) {
                    continue;
                }
                for (Map.Entry<String, byte[]> finger : fingers.entrySet()) {
                    ContentValues tpl = new ContentValues();
                    tpl.put("employee_id", employeeId);
                    tpl.put("finger_name", finger.getKey());
                    tpl.put("data", finger.getValue());
                    db.insertWithOnConflict("templates", null, tpl, SQLiteDatabase.CONFLICT_REPLACE);
                }
            }
            db.setTransactionSuccessful();
        } finally {
            db.endTransaction();
        }
    }

    public List<Employee> loadEmployees() {
        List<Employee> employees = new ArrayList<>();
        SQLiteDatabase db = getReadableDatabase();
        Cursor cursor = db.query("employees", null, null, null, null, null, "last_name, first_name");
        try {
            while (cursor.moveToNext()) {
                Employee employee = new Employee();
                employee.setId(cursor.getInt(cursor.getColumnIndexOrThrow("id")));
                employee.setFirstName(cursor.getString(cursor.getColumnIndexOrThrow("first_name")));
                employee.setLastName(cursor.getString(cursor.getColumnIndexOrThrow("last_name")));
                employee.setMiddleName(cursor.getString(cursor.getColumnIndexOrThrow("middle_name")));
                employee.setNin(cursor.getString(cursor.getColumnIndexOrThrow("nin")));
                employee.setBiometricEnrolled(true);
                employees.add(employee);
            }
        } finally {
            cursor.close();
        }
        return employees;
    }

    public Map<Integer, Map<String, byte[]>> loadTemplates() {
        Map<Integer, Map<String, byte[]>> allTemplates = new HashMap<>();
        SQLiteDatabase db = getReadableDatabase();
        Cursor cursor = db.query("templates", null, null, null, null, null, "employee_id");
        try {
            while (cursor.moveToNext()) {
                int employeeId = cursor.getInt(cursor.getColumnIndexOrThrow("employee_id"));
                String fingerName = cursor.getString(cursor.getColumnIndexOrThrow("finger_name"));
                byte[] data = cursor.getBlob(cursor.getColumnIndexOrThrow("data"));
                if (!allTemplates.containsKey(employeeId)) {
                    allTemplates.put(employeeId, new HashMap<String, byte[]>());
                }
                allTemplates.get(employeeId).put(fingerName, data);
            }
        } finally {
            cursor.close();
        }
        return allTemplates;
    }

    public boolean hasData() {
        SQLiteDatabase db = getReadableDatabase();
        Cursor cursor = db.rawQuery("SELECT COUNT(*) FROM templates", null);
        try {
            if (cursor.moveToFirst()) {
                return cursor.getInt(0) > 0;
            }
        } finally {
            cursor.close();
        }
        return false;
    }

    public void setSyncVersion(String version) {
        ContentValues values = new ContentValues();
        values.put("key", "version");
        values.put("value", version != null ? version : "");
        SQLiteDatabase db = getWritableDatabase();
        db.insertWithOnConflict("sync_meta", null, values, SQLiteDatabase.CONFLICT_REPLACE);
    }

    public String getSyncVersion() {
        SQLiteDatabase db = getReadableDatabase();
        Cursor cursor = db.query("sync_meta", new String[]{"value"}, "key = ?", new String[]{"version"}, null, null, null);
        try {
            if (cursor.moveToFirst()) {
                return cursor.getString(0);
            }
        } finally {
            cursor.close();
        }
        return null;
    }

    public void clearSyncVersion() {
        SQLiteDatabase db = getWritableDatabase();
        db.delete("sync_meta", "key = ?", new String[]{"version"});
    }

    public void clearAll() {
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            db.delete("employees", null, null);
            db.delete("templates", null, null);
            db.delete("sync_meta", null, null);
            db.setTransactionSuccessful();
        } finally {
            db.endTransaction();
        }
    }

    public int countTemplates() {
        SQLiteDatabase db = getReadableDatabase();
        Cursor cursor = db.rawQuery("SELECT COUNT(*) FROM templates", null);
        try {
            if (cursor.moveToFirst()) {
                return cursor.getInt(0);
            }
        } finally {
            cursor.close();
        }
        return 0;
    }

    public static byte[] decodeTemplate(String base64) {
        if (base64 == null || base64.isEmpty()) {
            return null;
        }
        try {
            return Base64.decode(base64.trim(), Base64.NO_WRAP);
        } catch (IllegalArgumentException firstError) {
            try {
                return Base64.decode(base64.trim(), Base64.DEFAULT);
            } catch (IllegalArgumentException secondError) {
                Log.w(TAG, "Template base64 invalide");
                return null;
            }
        }
    }
}
