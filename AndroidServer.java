package com.example.shivanjali.androidsocketserver;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintStream;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;
import java.util.Enumeration;
import java.util.logging.Logger;

import android.media.MediaPlayer;
import android.os.Bundle;
import android.app.Activity;
import android.provider.MediaStore;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

/*
 // This is the Android Sink
 //@Author: Shivanjali
  */

public class AndroidServer extends Activity {

    //Declaration section

    //Layout Elements declaration
    TextView info, infoip, msg;
    String message = "";
    EditText client;
    private Button buttonSubmit;
    private String clientCount;
    private Button buttonClear;

    //Declare socket variable
    ServerSocket serverSocket;

    //Declare media player variable
    MediaPlayer mp;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        //Set layout as content_android_Server.xml
        setContentView(R.layout.content_android_server);

        //Extract ID from the layout
        info = (TextView) findViewById(R.id.info);
        infoip = (TextView) findViewById(R.id.infoip);
        msg = (TextView) findViewById(R.id.msg);
        client=(EditText) findViewById(R.id.editClient);
        buttonSubmit=(Button) findViewById(R.id.buttonSubmit);
        buttonClear=(Button) findViewById(R.id.buttonClear);

        //Initialize media player
        mp=MediaPlayer.create(AndroidServer.this, R.raw.school);

        //Set the IP address of the server in the plaintext view
        infoip.setText(getIpAddress());

        //Listener for submit button
        buttonSubmit.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {
                clientCount=client.getText().toString();
                client.setEnabled(false);
                buttonSubmit.setEnabled(false);
            }
        });

        //Listener for Clear button
        buttonClear.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {

                mp.pause();
            }
        });

        //Create socket and start listening
        Thread socketServerThread = new Thread(new SocketServerThread());
        socketServerThread.start();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();


    }

    private class SocketServerThread extends Thread {

        static final int SocketServerPORT = 1024;
        int count = 0;

        @Override
        public void run() {
            try {
                //Create socket
                serverSocket = new ServerSocket(SocketServerPORT);

                //Update the port on the layout
                AndroidServer.this.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {
                        info.setText("I'm waiting here: "
                                + serverSocket.getLocalPort());
                    }
                });

                while (true) {
                    //Accept connection from client
                    Socket socket = serverSocket.accept();
                    count++;
                    message += "#" + count + " from " + socket.getInetAddress()
                            + ":" + socket.getPort() + "\n";

                    //Set the text view with the client IP and the port from which it is sending message
                    AndroidServer.this.runOnUiThread(new Runnable() {

                        @Override
                        public void run() {
                            msg.setText(message);
                        }
                    });

                    //Send reply to the client
                    SocketServerReplyThread socketServerReplyThread = new SocketServerReplyThread(
                            socket, count);
                    socketServerReplyThread.run();

                }
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
        }

    }

    private class SocketServerReplyThread extends Thread {

        private Socket hostThreadSocket;
        int cnt;

        SocketServerReplyThread(Socket socket, int c) {
            hostThreadSocket = socket;
            cnt = c;
        }

        @Override
        public void run() {
            OutputStream outputStream;
            InputStream inputStream;
            String msgReply = "Setup Clients" + cnt;

            try {
                outputStream = hostThreadSocket.getOutputStream();
                inputStream = hostThreadSocket.getInputStream();
                PrintStream printStream = new PrintStream(outputStream);

                //Send "Raise Alarm" to client after the setup phase
                if(cnt>Integer.parseInt(clientCount)+1){
                    msgReply = "Raise Alarm";
                    printStream.print(msgReply);
                    mp.start();

                }
                else
                    printStream.print(msgReply);
                printStream.close();

                message += "replayed: " + msgReply + "\n";
                //Set text message on the actions
                AndroidServer.this.runOnUiThread(new Runnable() {

                    @Override
                    public void run() {
                        msg.setText(message);
                    }
                });

            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
                message += "Something wrong! " + e.toString() + "\n";
            }

            AndroidServer.this.runOnUiThread(new Runnable() {

                @Override
                public void run() {
                    msg.setText(message);
                }
            });
        }

    }

    //Return the IP address of the server
    private String getIpAddress() {
        String ip = "";
        try {
            //Get all interfaces of the server
            Enumeration<NetworkInterface> enumNetworkInterfaces = NetworkInterface
                    .getNetworkInterfaces();
            while (enumNetworkInterfaces.hasMoreElements()) {
                NetworkInterface networkInterface = enumNetworkInterfaces
                        .nextElement();
                //Get the enumeration of IP address of the server
                Enumeration<InetAddress> enumInetAddress = networkInterface
                        .getInetAddresses();
                while (enumInetAddress.hasMoreElements()) {
                    InetAddress inetAddress = enumInetAddress.nextElement();

                    if (inetAddress.isSiteLocalAddress()) {
                        ip += "SiteLocalAddress: "
                                + inetAddress.getHostAddress() + "\n";
                    }

                }

            }

        } catch (SocketException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
            ip += "Something Wrong! " + e.toString() + "\n";
        }

        return ip;
    }
}