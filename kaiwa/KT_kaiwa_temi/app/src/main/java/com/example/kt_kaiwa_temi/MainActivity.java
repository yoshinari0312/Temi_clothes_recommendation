package com.example.kt_kaiwa_temi;

import androidx.appcompat.app.AppCompatActivity;

import android.annotation.SuppressLint;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;

import com.robotemi.sdk.Robot;
import com.robotemi.sdk.TtsRequest;
import com.robotemi.sdk.listeners.OnRobotReadyListener;

import org.jetbrains.annotations.NotNull;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.LinkedList;
import java.util.Queue;


public class MainActivity extends AppCompatActivity implements OnRobotReadyListener{

    private static final String TAG = MainActivity.class.getSimpleName();
    private static Robot mRobot;
    int portNum = 5530;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize robot instance
        mRobot = Robot.getInstance();

    }
    @Override
    protected void onStart() {
        super.onStart();

        // Add robot event listeners
        mRobot.addOnRobotReadyListener(this);
    }

    @Override
    protected void onStop() {
        super.onStop();

        // Remove robot event listeners
        mRobot.removeOnRobotReadyListener(this);
    }

    @Override
    public void onRobotReady(boolean isReady) {
        if (isReady) {
            Log.i(TAG, "Robot is ready");
            mRobot.hideTopBar(); // hide temi's ActionBar when skill is active

            TtsRequest ttsRequest = TtsRequest.create("プログラムを起動しました", false, TtsRequest.Language.JA_JP);
            mRobot.speak(ttsRequest);

            new TCPServer().execute();
        }
    }

    // ネットワーク操作はメインスレッドでやるとエラーが出るので、非同期関数で完全にラップする
    private class TCPServer extends AsyncTask<Void, Void, Void> {
        String result;
        @SuppressLint("WrongThread")
        @Override
        protected Void doInBackground(Void... voids) {
            try (ServerSocket server = new ServerSocket(portNum)) {
                while (true) {
                    try {
                        // -----------------------------------------
                        // 2.クライアントからの接続を待ち受け（accept）
                        // -----------------------------------------
                        Socket sc = server.accept();
                        Log.d("TCP status", "connected");
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

                                // Declare a queue of phrases
                                final Queue<String> queue = new LinkedList<>();
                                queue.add(received);
                                queue.add(""); // ダミーのキュー

                                // Register TTS listener
                                mRobot.addTtsListener(new Robot.TtsListener() {
                                    @Override
                                    public void onTtsStatusChanged(@NotNull TtsRequest ttsRequest) {
                                        if (ttsRequest.getStatus() == TtsRequest.Status.COMPLETED) {
                                            if (!queue.isEmpty()) {
                                                mRobot.speak(TtsRequest.create(queue.remove()));
                                            }
                                        }
                                    }
                                });

                                // Command robot to speak
                                mRobot.speak(TtsRequest.create(queue.remove(), false, TtsRequest.Language.JA_JP));

                                // speakメソッドは非同期なので、キューが空になるまで（喋り終わるまで）待つ
                                while(!queue.isEmpty()){}
                                bw.write("OK"+"\n");
                                bw.flush();
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
            return null;
        }
        @Override
        protected void onPostExecute(Void aVoid) {
            //textMessage.setText(result);
            //textLoad.setText("Finished");
            super.onPostExecute(aVoid);
        }
    }
}