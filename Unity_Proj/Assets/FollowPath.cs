using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class FollowPath : MonoBehaviour
{
    public GameObject marker;
    public GameObject[] waypoints;

    public float markerSpeed = 0.2f;

    private int nextWaypoint;

    private float startTime;
    private float journeyLength;

    public GameObject manager;


    // Start is called before the first frame update
    void Start()
    {
        nextWaypoint = 0;
        marker.transform.position = waypoints[0].transform.position;
    }

    // Update is called once per frame
    void Update()
    {

    }

    private void FixedUpdate()
    {
        if (manager.GetComponent<ExperimentManager>().currentPhase == enums.ExperimentPhases.RUNNING)
        {
            //if the marker reached the waypoint, go to the next one
            if (marker.transform.position == waypoints[nextWaypoint].transform.position)
            {
                if (nextWaypoint + 1 == waypoints.Length) //you are done
                {
                    StartCoroutine(StopExperiment());
                    return; 
                }
                nextWaypoint++;
                startTime = Time.time;
                journeyLength = Vector3.Distance(marker.transform.position, waypoints[nextWaypoint].transform.position);
            }

            //Lerp
            float distCovered = (Time.time - startTime) * markerSpeed;
            float fractionOfJourney = distCovered / journeyLength;
            marker.transform.position = Vector3.Lerp(waypoints[nextWaypoint - 1].transform.position, waypoints[nextWaypoint].transform.position, fractionOfJourney);
        }

    }

    public IEnumerator StartExperiment()
    {
        Debug.Log("Starting Experiment");
        //timer
        manager.GetComponent<ExperimentManager>().textFieldComp.text = "3";
        yield return new WaitForSeconds(1);
        manager.GetComponent<ExperimentManager>().textFieldComp.text = "2";
        yield return new WaitForSeconds(1);
        manager.GetComponent<ExperimentManager>().textFieldComp.text = "1";
        yield return new WaitForSeconds(1);
        //Start the marker
        manager.GetComponent<ExperimentManager>().currentPhase = enums.ExperimentPhases.RUNNING;
        startTime = Time.time;
        journeyLength = Vector3.Distance(marker.transform.position, waypoints[nextWaypoint].transform.position);
    }

    public IEnumerator StopExperiment()
    {
        manager.GetComponent<ExperimentManager>().currentPhase = enums.ExperimentPhases.FINISHING;
        manager.GetComponent<ExperimentManager>().textFieldComp.text = "Prepare for the next run\nGo back to the beginning";
        //TODO: Save the log

        yield return new WaitForSeconds(3);
        //rest script
        marker.transform.position = waypoints[0].transform.position;
        nextWaypoint = 0;
        manager.GetComponent<ExperimentManager>().currentPhase = enums.ExperimentPhases.FINISHED;



    }
}
