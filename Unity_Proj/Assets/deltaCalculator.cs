using extOSC;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class deltaCalculator : MonoBehaviour
{
    public GameObject marker;
    public GameObject hitPoint;
    float scaleFactor = 100.0f;

    private int[] NESW;
    public List<OSCValue> osc_NESW;

    public GameObject manager;

    // Experiment details. Used for logging.
    public int pressureReceived = 0;

    // Start is called before the first frame update
    void Start()
    {
        NESW = new int[4];
        osc_NESW = new List<OSCValue>(4);
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnCollisionStay(Collision collision)
    {
        hitPoint.transform.position = collision.contacts[0].point;
        int distance = (int)(scaleFactor * Vector3.Distance(marker.transform.position, collision.contacts[0].point));

        if (distance < 10 && manager.GetComponent<ExperimentManager>().currentPhase == enums.ExperimentPhases.PREPARING)
        {
            manager.GetComponent<ExperimentManager>().currentPhase = enums.ExperimentPhases.TIMER;
            StartCoroutine(GetComponent<FollowPath>().StartExperiment());            
        }
            

        //Distances North-South and West-East
        int distanceNS = (int)(scaleFactor * (marker.transform.position.y - collision.contacts[0].point.y));
        int distanceWE = (int)(scaleFactor * (marker.transform.position.z - collision.contacts[0].point.z));

        NESW[0] = distanceNS < 0 ? -distanceNS : 0; //north
        NESW[1] = distanceWE >= 0 ? distanceWE : 0; //east
        NESW[2] = distanceNS >= 0 ? distanceNS : 0; //south
        NESW[3] = distanceWE < 0 ? -distanceWE : 0; //west

        //Pack into an OSCArray
        osc_NESW.Clear();
        osc_NESW.Add(new OSCValue(OSCValueType.Int, NESW[0]));
        osc_NESW.Add(new OSCValue(OSCValueType.Int, NESW[1]));
        osc_NESW.Add(new OSCValue(OSCValueType.Int, NESW[2]));
        osc_NESW.Add(new OSCValue(OSCValueType.Int, NESW[3]));

        //Debug.Log(NESW[0] + ", " + NESW[1] + ", " + NESW[2] + ", " + NESW[3]);
        //Debug.Log("DistanceNS: " + distanceNS);
        //Debug.Log("DistanceWE: " + distanceWE);

        //TODO: Log the values: N, E, S, W, pressureReceived

    }

}
