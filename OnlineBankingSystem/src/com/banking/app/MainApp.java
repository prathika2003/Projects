package com.banking.app;

import java.util.Scanner;

public class MainApp {

    public static void main(String[] args) throws Exception {

        Scanner sc = new Scanner(System.in);
        BankOperations bank = new BankOperations();

        while (true) {
            System.out.println("\n--- ONLINE BANKING SYSTEM ---");
            System.out.println("1. Register");
            System.out.println("2. Login");
            System.out.println("3. Exit");
            System.out.print("Choose: ");
            int ch = sc.nextInt();

            if (ch == 1) {
                bank.registerUser();
            }
            else if (ch == 2) {
                long acc = bank.login();
                if (acc != -1) {
                    while (true) {
                        System.out.println("\n1.Balance 2.Deposit 3.Withdraw 4.Transfer 5.History 6.Logout");
                        int op = sc.nextInt();
                        if (op == 1) bank.checkBalance(acc);
                        else if (op == 2) bank.deposit(acc);
                        else if (op == 3) bank.withdraw(acc);
                        else if (op == 4) bank.transfer(acc);
                        else if (op == 5) bank.viewTransactions(acc);
                        else break;
                    }
                }
            }
            else {
                System.exit(0);
            }
        }
    }
}
