using extOSC;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class deltaCalculator : MonoBehaviour
{
    public GameObject marker;
    public GameObject hitPoint;
    float scaleFactor = 100.0f;

    public int OSC_N = 0, OSC_S = 0, OSC_E = 0, OSC_W = 0;

    public GameObject manager;

    // Experiment details. Used for logging.
    public int pressureReceived = 0;

    // Start is called before the first frame update
    void Start()
    {
    }

    // Update is called once per frame
    void Update()
    {

    }

    private void OnCollisionStay(Collision collision)
    {
        // Move the red hitpoint
        hitPoint.transform.position = collision.contacts[0].point;


        // Compute the distance on the axis
        int distanceNS = (int)(scaleFactor * (marker.transform.position.y - collision.contacts[0].point.y));
        int distanceWE = (int)(scaleFactor * (marker.transform.position.z - collision.contacts[0].point.z));

        // Compute the cartesian distance, not considering depth
        int distance = (int)Mathf.Sqrt(Mathf.Pow(distanceNS, 2) + Mathf.Pow(distanceWE, 2));

        if (manager.GetComponent<ExperimentManager>().currentPhase == enums.ExperimentPhases.PREPARING && distance < 10)
        {
            manager.GetComponent<ExperimentManager>().currentPhase = enums.ExperimentPhases.TIMER;
            StartCoroutine(GetComponent<FollowPath>().StartExperiment());
        }
        else if (manager.GetComponent<ExperimentManager>().currentPhase == enums.ExperimentPhases.RUNNING)
        {
            OSC_N = distanceNS < 0 ? -distanceNS : 0; //north
            OSC_E = distanceWE > 0 ? distanceWE : 0; //east
            OSC_S = distanceNS > 0 ? distanceNS : 0; //south
            OSC_W = distanceWE < 0 ? -distanceWE : 0; //west
        }
        else
        {
            // Avoid feedback in PD
            OSC_N = 0; OSC_S = 0; OSC_E = 0; OSC_W = 0;
        }

        //Debug.Log(NESW[0] + ", " + NESW[1] + ", " + NESW[2] + ", " + NESW[3]);
        //Debug.Log("DistanceNS: " + distanceNS);
        //Debug.Log("DistanceWE: " + distanceWE);

        //TODO: Log the values: N, E, S, W, pressureReceived

    }

}
