package com.example.kt_fukusuisen_temi;

import androidx.appcompat.app.AppCompatActivity;

import android.annotation.SuppressLint;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.widget.ImageView;

import com.robotemi.sdk.Robot;
import com.robotemi.sdk.TtsRequest;
import com.robotemi.sdk.listeners.OnRobotReadyListener;
import com.robotemi.sdk.listeners.OnMovementStatusChangedListener;
import com.robotemi.sdk.navigation.listener.OnDistanceToDestinationChangedListener;
import com.robotemi.sdk.navigation.model.Position;

import org.jetbrains.annotations.NotNull;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.IDN;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.LinkedList;
import java.util.Queue;
import java.util.concurrent.CountDownLatch;

public class MainActivity extends AppCompatActivity implements OnRobotReadyListener, OnDistanceToDestinationChangedListener {

    private static final String TAG = MainActivity.class.getSimpleName();
    private static Robot mRobot;
    private boolean isMoving;
    private Queue<String> ttsQueue;
    private String currentDestination;  // 現在の目的地を保持する変数
    private String pastDestination;
    private int id;
    int portNum = 5531;
    private String KAWASAKIsan_IP = "192.168.1.84";
    private int time_count = 0;

    private boolean isSendData = true; // action graphが狂ってたらこれをfalseにする。


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize robot instance
        mRobot = Robot.getInstance();
        ttsQueue = new LinkedList<>();
        isMoving = false;

        // TTSリスナーの登録（ここで一回やるだけでいい）
        mRobot.addTtsListener(new Robot.TtsListener() {
            @Override
            public void onTtsStatusChanged(@NotNull TtsRequest ttsRequest) {
                if (ttsRequest.getStatus() == TtsRequest.Status.COMPLETED) {
                    processNextTTSQueue();
                }
            }
        });

    }
    @Override
    protected void onStart() {
        super.onStart();

        // Add robot event listeners
        mRobot.addOnRobotReadyListener(this);
//        mRobot.addOnMovementStatusChangedListener(this);
        mRobot.addOnDistanceToDestinationChangedListener(this);
    }

    @Override
    protected void onStop() {
        super.onStop();

        // Remove robot event listeners
        mRobot.removeOnRobotReadyListener(this);
//        mRobot.removeOnMovementStatusChangedListener(this);
        mRobot.removeOnDistanceToDestinationChangedListener(this);
    }

    @Override
    public void onRobotReady(boolean isReady) {
        if (isReady) {
            Log.i(TAG, "Robot is ready");
            mRobot.hideTopBar(); // hide temi's ActionBar when skill is active

            TtsRequest ttsRequest = TtsRequest.create("プログラムを起動しました", false, TtsRequest.Language.JA_JP);
            mRobot.speak(ttsRequest);


            //temiの顔
            // ImageViewの用意
            ImageView myImage= findViewById(R.id.myImage);
            // 画像名
            String imageName = "temi_face";
            // 画像のリソースIDを取得
            int resId = getResources().getIdentifier(imageName, "drawable", getPackageName());
            // ImageViewに画像をセット
            myImage.setImageResource(resId);
            pastDestination = "";


            new sendData().execute();


            // メイン(UI)スレッドでHandlerのインスタンスを生成する
            final Handler handler = new Handler();


            new Thread(new Runnable() {
                @Override
                public void run() {

                    try (ServerSocket server = new ServerSocket(portNum)) {
                        while (true) {
                            try {
                                // -----------------------------------------
                                // 2.クライアントからの接続を待ち受け（accept）
                                // -----------------------------------------
                                Socket sc = server.accept();
                                Log.d("TCP status", sc.toString());
                                BufferedReader reader = null;
                                BufferedWriter bw = null;

                                // -----------------------------------------
                                // 3.クライアントからの接続ごとにスレッドで通信処理を実行
                                // -----------------------------------------
                                try {
                                    // クライアントからの受取用
                                    reader = new BufferedReader(new InputStreamReader(sc.getInputStream()));
                                    System.out.println(reader);
                                    // クライアントに送る用
                                    bw = new BufferedWriter(new OutputStreamWriter(sc.getOutputStream()));

                                    String received = reader.readLine();

                                    if (received != null) {
                                        System.out.println(received);
                                        Log.i(TAG, received);

                                        String[] command = received.split(":");

                                        // 発話とジェスチャを同時にさせる
                                        if (command[1].equals("none")) {
                                            // Handlerを使用してメイン(UI)スレッドに処理を依頼する
                                            handler.post(new Runnable() {
                                                @Override
                                                public void run() {
                                                    //temiの顔
                                                    // ImageViewの用意
                                                    ImageView myImage= findViewById(R.id.myImage);
                                                    // 画像名
                                                    String imageName = "temi_face";
                                                    // 画像のリソースIDを取得
                                                    int resId = getResources().getIdentifier(imageName, "drawable", getPackageName());
                                                    // ImageViewに画像をセット
                                                    myImage.setImageResource(resId);
                                                }
                                            });

                                            ttsQueue.add(command[0]);
                                            ttsQueue.add(""); // ダミーのキュー

                                            // Command robot to speak
                                            processNextTTSQueue();

                                            // speakメソッドは非同期なので、キューが空になるまで（喋り終わるまで）待つ
                                            while (!ttsQueue.isEmpty()) {
                                            }
                                            bw.write("OK" + "\n");
                                            bw.flush();

                                        }
                                        else if(command[1].equals("picture")){
                                            // Handlerを使用してメイン(UI)スレッドに処理を依頼する
                                            handler.post(new Runnable() {
                                                @Override
                                                public void run() {

                                                    //服の画像
                                                    // ImageViewの用意
                                                    ImageView myImage= findViewById(R.id.myImage);
                                                    // 画像名
                                                    String imageName = "f" + command[2];
                                                    // 画像のリソースIDを取得
                                                    int resId = getResources().getIdentifier(imageName, "drawable", getPackageName());
                                                    // ImageViewに画像をセット
                                                    myImage.setImageResource(resId);
                                                }
                                            });


                                            ttsQueue.add(command[0]);
                                            ttsQueue.add(""); // ダミーのキュー

                                            // Command robot to speak
                                            processNextTTSQueue();

                                            // speakメソッドは非同期なので、キューが空になるまで（喋り終わるまで）待つ
                                            while (!ttsQueue.isEmpty()) {
                                            }
                                            bw.write("OK" + "\n");
                                            bw.flush();

                                        }
                                        else if(command[1].equals("move")){
                                            // Handlerを使用してメイン(UI)スレッドに処理を依頼する
                                            handler.post(new Runnable() {
                                                @Override
                                                public void run() {
                                                    //temiの顔
                                                    // ImageViewの用意
                                                    ImageView myImage= findViewById(R.id.myImage);
                                                    // 画像名
                                                    String imageName = "temi_face";
                                                    // 画像のリソースIDを取得
                                                    int resId = getResources().getIdentifier(imageName, "drawable", getPackageName());
                                                    // ImageViewに画像をセット
                                                    myImage.setImageResource(resId);
                                                }
                                            });

                                            id = Integer.parseInt(command[2]);
                                            isMoving = false;
                                            System.out.println("id is:" + id);
                                            CountDownLatch latch = new CountDownLatch(1);

                                            String[] move_text = command[0].split(";");

                                            ttsQueue.add(move_text[0]);
                                            ttsQueue.add(""); // ダミーのキュー

                                            processNextTTSQueue();

                                            while (!ttsQueue.isEmpty()) {
                                                Thread.sleep(100);
                                            }

                                            isMoving = true;
                                            time_count = 0;

//                                            if(id == 70){
//                                                currentDestination = "服1";
//                                            }else if(id == 71){
//                                                currentDestination = "服2";
//                                            }else if(1 <= id && id <= 32){
//                                                currentDestination = "ディスプレイ1";
//                                            }else if(33 <= id && id <= 66){
//                                                currentDestination = "ディスプレイ2";
//                                            }else{
//                                                currentDestination = "ディスプレイ3";
//                                            }

                                            if(1 <= id && id <= 33){
                                                currentDestination = "ディスプレイ1";
                                            }else if(34 <= id && id <= 67){
                                                currentDestination = "ディスプレイ2";
                                            }else{
                                                currentDestination = "ディスプレイ3";
                                            }

                                            if(!(currentDestination.equals(pastDestination))){
                                                mRobot.goTo(currentDestination);

                                                new Thread(() -> {
                                                    try {
                                                        while (isMoving) {
                                                            if (time_count >= 10){
                                                                isMoving = false;
                                                            }
                                                            time_count += 1;
                                                            Log.i(TAG, Integer.toString(time_count));
                                                            Log.i(TAG, "Waiting for movement to complete...");
                                                            if (isSendData == true){
                                                                new sendData().execute();
                                                            }
                                                            Thread.sleep(500);
                                                        }
                                                        ttsQueue.add(move_text[1]);
                                                        ttsQueue.add(""); // ダミーのキュー
                                                        processNextTTSQueue();
                                                    } catch (InterruptedException e) {
                                                        e.printStackTrace();
                                                    }
                                                    latch.countDown();
                                                }).start();

                                                latch.await();
                                            }else{
                                                isMoving = false;
                                                ttsQueue.add(move_text[1]);
                                                ttsQueue.add(""); // ダミーのキュー
                                                processNextTTSQueue();
                                            }

                                            while (!ttsQueue.isEmpty()) {
                                                Thread.sleep(100);
                                            }
                                            pastDestination = currentDestination;

                                            bw.write("OK" + "\n");
                                            bw.flush();
                                        }
                                    }
                                } catch (Exception e) {
                                    e.printStackTrace();
                                } finally {
                                    // リソースの解放
                                    reader.close();
                                    bw.close();
                                    sc.close();
                                }
                            } catch (Exception ex) {
                                ex.printStackTrace();
                                break;
                            }
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                    }

                }
            }).start();


        }
    }

    // 動作が終わったらisMovingをfalseにする
//    @Override
//    public void onMovementStatusChanged(@NotNull String type, @NotNull String status){
//        Log.i(TAG, "Movement status changed: " + status);
//        if (status.equals(OnMovementStatusChangedListener.STATUS_COMPLETE))  {
//            isMoving = false;
//            processNextTTSQueue();
//        }
//    }
    @Override
    public void onDistanceToDestinationChanged(@NotNull String location, float distance) {
        time_count = 0;
        Log.i(TAG, "Distance to destination (" + location + "): " + distance);
        if (location.equals(currentDestination) && distance < 1.0 && distance != 0.0) { // 0.5メートル未満の場合
            isMoving = false;
        }
    }

    // キューから1つ取り出して喋る
    private void processNextTTSQueue() {
        if (!ttsQueue.isEmpty() && !isMoving) {
            String nextTTS = ttsQueue.poll();
            if (nextTTS != null && !nextTTS.isEmpty()) {
                mRobot.speak(TtsRequest.create(nextTTS, false, TtsRequest.Language.JA_JP));
            }
        }
    }


        private class sendData extends AsyncTask<Void, Void, Void> {
        String result;
        @SuppressLint("WrongThread")
        @Override
        protected Void doInBackground(Void... voids) {
            try (Socket socket2 = new Socket(KAWASAKIsan_IP, 5540);
                 PrintWriter writer = new PrintWriter(socket2.getOutputStream(), true);
                 BufferedReader reader = new BufferedReader(new InputStreamReader(socket2.getInputStream()));
                 // キーボード入力用のリーダーの作成
                 BufferedReader keyboard = new BufferedReader(new InputStreamReader(System.in)))
            {
                float x = mRobot.getPosition().getX();
                float y = mRobot.getPosition().getY();
                writer.println(Double.toString(x) + ", " + Double.toString(y));

            } catch (Exception e) {
                e.printStackTrace();
            }
            return null;
        }
        @Override
        protected void onPostExecute(Void aVoid) {

        }
    }

//    // いらない
//    // ネットワーク操作はメインスレッドでやるとエラーが出るので、非同期関数で完全にラップする
//    private class TCPServer extends AsyncTask<Void, Void, Void> {
//        String result;
//        @SuppressLint("WrongThread")
//        @Override
//        protected Void doInBackground(Void... voids) {
//            try (ServerSocket server = new ServerSocket(portNum)) {
//                while (true) {
//                    try {
//                        // -----------------------------------------
//                        // 2.クライアントからの接続を待ち受け（accept）
//                        // -----------------------------------------
//                        Socket sc = server.accept();
//                        Log.d("TCP status", "connected");
//                        BufferedReader reader = null;
//                        BufferedWriter bw = null;
//                        // -----------------------------------------
//                        // 3.クライアントからの接続ごとにスレッドで通信処理を実行
//                        // -----------------------------------------
//                        try {
//                            // クライアントからの受取用
//                            reader = new BufferedReader(new InputStreamReader(sc.getInputStream()));
//                            System.out.println(reader);
//                            // クライアントに送る用
//                            bw = new BufferedWriter(new OutputStreamWriter(sc.getOutputStream()));
//
//                            String received = reader.readLine();
//
//                            if (received != null) {
//                                System.out.println(received);
//                                Log.i(TAG, received);
//
//                                String[] command = received.split(":");
//
//                                // 発話とジェスチャを同時にさせる
//                                if (command[1].equals("none")) {
//                                    ttsQueue.add(command[0]);
//                                    ttsQueue.add(""); // ダミーのキュー
//
//                                    // Command robot to speak
//                                    processNextTTSQueue();
//
//                                    // speakメソッドは非同期なので、キューが空になるまで（喋り終わるまで）待つ
//                                    while (!ttsQueue.isEmpty()) {
//                                    }
//                                    bw.write("OK" + "\n");
//                                    bw.flush();
//                                }
//                                else if(command[1].equals("picture")){
//
//
//                                    // 画像の表示
//
//
//                                    ttsQueue.add(command[0]);
//                                    ttsQueue.add(""); // ダミーのキュー
//
//                                    // Command robot to speak
//                                    processNextTTSQueue();
//
//                                    // speakメソッドは非同期なので、キューが空になるまで（喋り終わるまで）待つ
//                                    while (!ttsQueue.isEmpty()) {
//                                    }
//                                    bw.write("OK" + "\n");
//                                    bw.flush();
//                                }
//                                else if(command[1].equals("move")){
//                                    int id = Integer.parseInt(command[2]);
//                                    System.out.println("id is:" + id);
//                                    CountDownLatch latch = new CountDownLatch(1);
//
//                                    String[] move_text = command[0].split(";");
//
//                                    ttsQueue.add(move_text[0]);
//                                    ttsQueue.add(""); // ダミーのキュー
//
//                                    processNextTTSQueue();
//
//                                    while (!ttsQueue.isEmpty()) {
//                                        Thread.sleep(100);
//                                    }
//
//                                    isMoving = true;
//                                    if(id == 70){
//                                        currentDestination = "服1";
//                                    }else if(id == 71){
//                                        currentDestination = "服2";
//                                    }else if(1 <= id && id <= 32){
//                                        currentDestination = "ディスプレイ1";
//                                    }else if(33 <= id && id <= 66){
//                                        currentDestination = "ディスプレイ2";
//                                    }else{
//                                        currentDestination = "ディスプレイ3";
//                                    }
//                                    mRobot.goTo(currentDestination);
//
//                                    new Thread(() -> {
//                                        try {
//                                            while (isMoving) {
//                                                Log.i(TAG, "Waiting for movement to complete...");
//                                                Thread.sleep(100);
//                                            }
//                                            ttsQueue.add(move_text[1]);
//                                            ttsQueue.add(""); // ダミーのキュー
//                                            processNextTTSQueue();
//                                        } catch (InterruptedException e) {
//                                            e.printStackTrace();
//                                        }
//                                        latch.countDown();
//                                    }).start();
//
//                                    latch.await();
//
//                                    while (!ttsQueue.isEmpty()) {
//                                        Thread.sleep(100);
//                                    }
//
//                                    bw.write("OK" + "\n");
//                                    bw.flush();
//                                }
//                            }
//                        } catch (Exception e) {
//                            e.printStackTrace();
//                        } finally {
//                            // リソースの解放
//                            reader.close();
//                            bw.close();
//                            sc.close();
//                        }
//                    } catch (Exception ex) {
//                        ex.printStackTrace();
//                        break;
//                    }
//                }
//            } catch (Exception e) {
//                e.printStackTrace();
//            }
//            return null;
//        }
//        @Override
//        protected void onPostExecute(Void aVoid) {
//            //textMessage.setText(result);
//            //textLoad.setText("Finished");
//            super.onPostExecute(aVoid);
//        }
//    }


}
