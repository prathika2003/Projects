package com.banking.app;

import java.sql.*;
import java.util.Scanner;

public class BankOperations {

    Scanner sc = new Scanner(System.in);
    Connection conn = DBConnection.getConnection();

    // 🔹 User Registration
    public void registerUser() throws Exception {
        System.out.print("Enter Name: ");
        String name = sc.nextLine();

        System.out.print("Enter Email: ");
        String email = sc.nextLine();

        System.out.print("Enter Password: ");
        String pass = sc.nextLine();

        PreparedStatement ps = conn.prepareStatement(
                "INSERT INTO users(name,email,password) VALUES(?,?,?)",
                Statement.RETURN_GENERATED_KEYS);

        ps.setString(1, name);
        ps.setString(2, email);
        ps.setString(3, pass);
        ps.executeUpdate();

        ResultSet rs = ps.getGeneratedKeys();
        if (rs.next()) {
            int userId = rs.getInt(1);
            long accNo = System.currentTimeMillis();

            PreparedStatement ps2 = conn.prepareStatement(
                    "INSERT INTO accounts VALUES(?,?,?)");
            ps2.setLong(1, accNo);
            ps2.setInt(2, userId);
            ps2.setDouble(3, 0.0);
            ps2.executeUpdate();

            System.out.println("✅ Account Created Successfully!");
            System.out.println("Your Account Number: " + accNo);
        }
    }

    // 🔹 Login
    public long login() throws Exception {
        System.out.print("Enter Account Number: ");
        long accNo = sc.nextLong();
        sc.nextLine();

        System.out.print("Enter Password: ");
        String pass = sc.nextLine();

        PreparedStatement ps = conn.prepareStatement(
                "SELECT * FROM users u JOIN accounts a ON u.user_id=a.user_id WHERE a.account_no=? AND u.password=?");
        ps.setLong(1, accNo);
        ps.setString(2, pass);

        ResultSet rs = ps.executeQuery();
        if (rs.next()) {
            System.out.println("✅ Login Successful");
            return accNo;
        } else {
            System.out.println("❌ Invalid Login");
            return -1;
        }
    }

    // 🔹 Balance Inquiry
    public void checkBalance(long accNo) throws Exception {
        PreparedStatement ps = conn.prepareStatement(
                "SELECT balance FROM accounts WHERE account_no=?");
        ps.setLong(1, accNo);

        ResultSet rs = ps.executeQuery();
        if (rs.next()) {
            System.out.println("💰 Current Balance: " + rs.getDouble(1));
        }
    }

    // 🔹 Deposit
    public void deposit(long accNo) throws Exception {
        System.out.print("Enter Amount: ");
        double amt = sc.nextDouble();

        PreparedStatement ps = conn.prepareStatement(
                "UPDATE accounts SET balance=balance+? WHERE account_no=?");
        ps.setDouble(1, amt);
        ps.setLong(2, accNo);
        ps.executeUpdate();

        recordTransaction(accNo, "DEPOSIT", amt);
        System.out.println("✅ Amount Deposited");
    }

    // 🔹 Withdraw
    public void withdraw(long accNo) throws Exception {
        System.out.print("Enter Amount: ");
        double amt = sc.nextDouble();

        conn.setAutoCommit(false);

        PreparedStatement ps1 = conn.prepareStatement(
                "SELECT balance FROM accounts WHERE account_no=?");
        ps1.setLong(1, accNo);
        ResultSet rs = ps1.executeQuery();

        if (rs.next() && rs.getDouble(1) >= amt) {
            PreparedStatement ps2 = conn.prepareStatement(
                    "UPDATE accounts SET balance=balance-? WHERE account_no=?");
            ps2.setDouble(1, amt);
            ps2.setLong(2, accNo);
            ps2.executeUpdate();

            recordTransaction(accNo, "WITHDRAW", amt);
            conn.commit();
            System.out.println("✅ Withdrawal Successful");
        } else {
            conn.rollback();
            System.out.println("❌ Insufficient Balance");
        }
        conn.setAutoCommit(true);
    }

    // 🔹 Fund Transfer
    public void transfer(long fromAcc) throws Exception {
        System.out.print("Enter Receiver Account: ");
        long toAcc = sc.nextLong();

        System.out.print("Enter Amount: ");
        double amt = sc.nextDouble();

        conn.setAutoCommit(false);

        try {
            PreparedStatement debit = conn.prepareStatement(
                    "UPDATE accounts SET balance=balance-? WHERE account_no=? AND balance>=?");
            debit.setDouble(1, amt);
            debit.setLong(2, fromAcc);
            debit.setDouble(3, amt);

            if (debit.executeUpdate() == 0)
                throw new Exception("Insufficient Balance");

            PreparedStatement credit = conn.prepareStatement(
                    "UPDATE accounts SET balance=balance+? WHERE account_no=?");
            credit.setDouble(1, amt);
            credit.setLong(2, toAcc);
            credit.executeUpdate();

            recordTransaction(fromAcc, "TRANSFER-DEBIT", amt);
            recordTransaction(toAcc, "TRANSFER-CREDIT", amt);

            conn.commit();
            System.out.println("✅ Transfer Successful");
        } catch (Exception e) {
            conn.rollback();
            System.out.println("❌ Transfer Failed");
        }
        conn.setAutoCommit(true);
    }

    // 🔹 Transaction History
    public void viewTransactions(long accNo) throws Exception {
        PreparedStatement ps = conn.prepareStatement(
                "SELECT * FROM transactions WHERE account_no=?");
        ps.setLong(1, accNo);

        ResultSet rs = ps.executeQuery();
        System.out.println("---- Transaction History ----");
        while (rs.next()) {
            System.out.println(rs.getString(3) + " | " +
                               rs.getDouble(4) + " | " +
                               rs.getTimestamp(5));
        }
    }

    private void recordTransaction(long accNo, String type, double amt) throws Exception {
        PreparedStatement ps = conn.prepareStatement(
                "INSERT INTO transactions(account_no,txn_type,amount) VALUES(?,?,?)");
        ps.setLong(1, accNo);
        ps.setString(2, type);
        ps.setDouble(3, amt);
        ps.executeUpdate();
    }
}
