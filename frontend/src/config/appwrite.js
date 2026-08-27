import { Client, Account, Databases } from "appwrite"; 

const client = new Client();
client.setEndpoint("https://fra.cloud.appwrite.io/v1").setProject("6a85a35c0019ef21486b");

export const account = new Account(client);

export const database = new Databases(client, "6a85ad4800121fff71da");