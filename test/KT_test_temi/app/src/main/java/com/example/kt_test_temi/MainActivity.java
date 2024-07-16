package com.example.kt_test_temi;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.util.Log;

import com.robotemi.sdk.Robot;
import com.robotemi.sdk.listeners.OnRobotReadyListener;
import com.robotemi.sdk.navigation.model.Position;

public class MainActivity extends AppCompatActivity implements OnRobotReadyListener {
    private static Robot mRobot;
    private static final String TAG = MainActivity.class.getSimpleName();

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

            mRobot.goTo("ペッパー");

            float x = mRobot.getPosition().getX();
            float y = mRobot.getPosition().getY();
            float yaw = mRobot.getPosition().getYaw();
            int tilt = mRobot.getPosition().getTiltAngle();


            Log.i(TAG, Double.toString(x) + " / " + Double.toString(y) + " / " + Double.toString(yaw) + " / " + Integer.toString(tilt));


        }
    }
}