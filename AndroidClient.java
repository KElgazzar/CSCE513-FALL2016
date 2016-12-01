package com.example.shivanjali.androidclient;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.Socket;
import java.net.UnknownHostException;

import android.content.Intent;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.media.MediaPlayer;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.app.Activity;
import android.telephony.SmsManager;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

/*
 // This is the Android Sensor
 //@Author: Shivanjali
  */
public class AndroidClient extends Activity implements SensorEventListener {

    /*Declaration section*/
    //Layout variables
    TextView textResponse;
    EditText editTextAddress, editTextPort;
    Button buttonConnect, buttonClear;

    //Sensor variables
    private SensorManager mSensorManager;
    private Sensor mSensor;

    //Socket variable
    Socket socket;

    //Flag not to send data to sink
    int flag=0;

    //Variables for sending SMS
    SmsManager smsManager;
    EditText Number;
    String number;

    //variable for playing media
    MediaPlayer mp;

    /*
    Overridden methods of the class Sensor Event Listener
     */
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
    }

   //Detect intruder or proximity sensor
    public void onSensorChanged(SensorEvent event) {
        System.out.println("Sensor value is :" + event.values[0]);

        //Send the values to the sink if the IPaddress and port are retrieved from the text fields
        if(flag==1) {

                MyClientTask myClientTask = new MyClientTask(
                        editTextAddress.getText().toString(),
                        Integer.parseInt(editTextPort.getText().toString()));

                myClientTask.execute();


        }
    }
    protected void onPause() {
        super.onPause();
        mSensorManager.unregisterListener(this);
    }

    protected void onResume() {
        super.onResume();
        mSensorManager.registerListener(this, mSensor,
                SensorManager.SENSOR_DELAY_NORMAL);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        //Set layout as activity_android_client.xml
        setContentView(R.layout.activity_android_client);

        //Initialize Media player with Alarm sound
        mp=MediaPlayer.create(AndroidClient.this, R.raw.school);

        //Get individual ID of the Layout elements
        editTextAddress = (EditText)findViewById(R.id.address);
        editTextPort = (EditText)findViewById(R.id.port);
        buttonConnect = (Button)findViewById(R.id.connect);
        buttonClear = (Button)findViewById(R.id.clear);
        textResponse = (TextView)findViewById(R.id.response);
        Number = (EditText)findViewById(R.id.number);
        buttonConnect.setOnClickListener(buttonConnectOnClickListener);

        //Listener for Clear or Reset Button
        buttonClear.setOnClickListener(new OnClickListener() {

            @Override
            public void onClick(View v) {
                textResponse.setText("");
                //Pause the alarm sound
                mp.pause();
            }
        });

        //Declare the sensor variables to use proximity sensor
        mSensorManager = (SensorManager) getSystemService(SENSOR_SERVICE);
        mSensor = mSensorManager.getDefaultSensor(Sensor.TYPE_PROXIMITY);

        //Declare the sms variables
        smsManager = SmsManager.getDefault();

    }

    //Listener for connect button
    OnClickListener buttonConnectOnClickListener =
            new OnClickListener(){

                @Override
                public void onClick(View arg0) {
                    //Create a socket
                    MyClientTask myClientTask = new MyClientTask(
                            editTextAddress.getText().toString(),
                            Integer.parseInt(editTextPort.getText().toString()));

                    //Extract the phone number
                    number=Number.getText().toString();
                    if(Number.getText().equals(null))
                        number="+12564689279";

                    //Disable few of the layout elements
                    buttonConnect.setEnabled(false);
                    editTextAddress.setEnabled(false);
                    editTextPort.setEnabled(false);
                    Number.setEnabled(false);

                    //Connect to the server
                    myClientTask.execute();
                }};

    public class MyClientTask extends AsyncTask<Void, Void, Void> {

        //Initialization of class variables
        String dstAddress;
        int dstPort;
        String response = "";

        //Set the IP address and port
        MyClientTask(String addr, int port){
            dstAddress = addr;
            dstPort = port;
        }

        @Override
        protected Void doInBackground(Void... arg0) {

            socket = null;

            try {
                //Create Socket
                socket = new Socket(dstAddress, dstPort);

                ByteArrayOutputStream byteArrayOutputStream =
                        new ByteArrayOutputStream(1024);
                byte[] buffer = new byte[1024];

                int bytesRead;
                InputStream inputStream = socket.getInputStream();


                //Blocking receive
                while ((bytesRead = inputStream.read(buffer)) != -1){

                    byteArrayOutputStream.write(buffer, 0, bytesRead);
                    response += byteArrayOutputStream.toString("UTF-8");
                    System.out.println("Buffer" +response);
                    //Raise alarm after setup phase
                    if(response.equals("Raise Alarm")){

                        mp.start();
                        smsManager.sendTextMessage(number, null, "Intruder Alert!", null, null);

                    }
                }

            } catch (UnknownHostException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
                response = "UnknownHostException: " + e.toString();
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
                response = "IOException: " + e.toString();
            }finally{
                if(socket != null){
                    try {
                        socket.close();
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }
            }
            return null;
        }

        @Override
        protected void onPostExecute(Void result) {
            textResponse.setText(response);
            super.onPostExecute(result);
            flag=1;
        }




    }

}