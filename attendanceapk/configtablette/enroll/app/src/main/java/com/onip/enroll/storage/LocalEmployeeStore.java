package com.onip.enroll.storage;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import com.onip.enroll.models.Employee;
import java.util.ArrayList;
import java.util.List;

/** Cache local de la liste agents RH pour l'enrôlement offline. */
public class LocalEmployeeStore extends SQLiteOpenHelper {

    private static final String DB_NAME = "enroll_employees.db";
    private static final int DB_VERSION = 1;

    public LocalEmployeeStore(Context context) {
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
                        "nin TEXT, " +
                        "biometric_enrolled INTEGER DEFAULT 0" +
                        ")"
        );
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS employees");
        onCreate(db);
    }

    public void replaceAll(List<Employee> employees) {
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            db.delete("employees", null, null);
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
                    row.put("biometric_enrolled", employee.isBiometricEnrolled() ? 1 : 0);
                    db.insert("employees", null, row);
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
                employee.setBiometricEnrolled(cursor.getInt(cursor.getColumnIndexOrThrow("biometric_enrolled")) == 1);
                employees.add(employee);
            }
        } finally {
            cursor.close();
        }
        return employees;
    }

    public boolean hasData() {
        SQLiteDatabase db = getReadableDatabase();
        Cursor cursor = db.rawQuery("SELECT COUNT(*) FROM employees", null);
        try {
            if (cursor.moveToFirst()) {
                return cursor.getInt(0) > 0;
            }
        } finally {
            cursor.close();
        }
        return false;
    }

    public int countEmployees() {
        SQLiteDatabase db = getReadableDatabase();
        Cursor cursor = db.rawQuery("SELECT COUNT(*) FROM employees", null);
        try {
            if (cursor.moveToFirst()) {
                return cursor.getInt(0);
            }
        } finally {
            cursor.close();
        }
        return 0;
    }

    public void clearAll() {
        SQLiteDatabase db = getWritableDatabase();
        db.delete("employees", null, null);
    }
}
