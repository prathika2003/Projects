package com.banking.app;
import java.sql.Connection;
import java.sql.DriverManager;

public class DBConnection {

    static Connection conn;

    public static Connection getConnection() {
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
            conn = DriverManager.getConnection(
                    "jdbc:mysql://localhost:3306/online_banking",
                    "root",
            		"Varsha@20");   // change password
        } catch (Exception e) {
            e.printStackTrace();
        }
        return conn;
    }
}
