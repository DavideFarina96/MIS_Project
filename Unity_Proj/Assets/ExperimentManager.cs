using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class ExperimentManager : MonoBehaviour
{
    public GameObject[] paths;
    private int FeedbackTypesLength = 4;
    private int repetitionsPerPath = 3;
    private int experimentsBetweenBreaks = 12;

    public bool isStarted = false;
    public enums.ExperimentPhases currentPhase = enums.ExperimentPhases.PREPARING;
    public int currentExperimentNumber = 0;
    public int currentFeedbackType = -1;

    public string OSC_experiment_message;

    public GameObject textField;
    public TMP_Text textFieldComp;

    private Experiment[] experiments;

    // Start is called before the first frame update
    void Start()
    {
        textFieldComp = textField.GetComponent<TMP_Text>();
        GenerateExperimentsList();
        
        isStarted = true;
    }

    // Update is called once per frame
    void FixedUpdate()
    {
        if (isStarted)
        {
            //Debug.Log("Current Phase: " + currentPhase);
            switch (currentPhase)
            {
                case enums.ExperimentPhases.PREPARING:
                    //Debug.Log("Now running experiment number " + currentExperimentNumber);
                    // Send feed back type to the OSC controller 
                    currentFeedbackType = (int)experiments[currentExperimentNumber].feedback;
                    // Actually start the experiment
                    experiments[currentExperimentNumber].path.SetActive(true);
                    textFieldComp.text = "Move your cursor near the blue ball to begin."; break;
                case enums.ExperimentPhases.RUNNING:
                    // Send experiment information to the OSC controller
                    OSC_experiment_message = experiments[currentExperimentNumber].ToString();
                    textFieldComp.text = "Follow the blue ball"; break;
                case enums.ExperimentPhases.FINISHED:
                    // Hide the path from the scene
                    experiments[currentExperimentNumber].path.SetActive(false);
                    currentExperimentNumber++;
                    currentPhase = enums.ExperimentPhases.PREPARING; break;
            }
        }
    }

    public void send_OSC_finished()
    {
        // Signal the OSC controller that the experiment has finished
        OSC_experiment_message = "FINISHED";
    }

    void GenerateExperimentsList()
    {
        //Generate the sequence of experiments
        experiments = new Experiment[paths.Length * FeedbackTypesLength * repetitionsPerPath];

        for (int i = 0; i < paths.Length; i++)
        {
            for (int j = 0; j < FeedbackTypesLength; j++)
            {
                for (int k = 0; k < repetitionsPerPath; k++)
                {
                    int index = (i * FeedbackTypesLength + j) * repetitionsPerPath + k;
                    experiments[index] = new Experiment(paths[i], (enums.FeedbackTypes)j, k + 1);
                }
            }
        }

        // Shuffle the experiments around
        Shuffle(experiments);
    }

    void Shuffle(Experiment[] experiments)
    {
        // Knuth shuffle algorithm :: courtesy of Wikipedia :)
        for (int t = 0; t < experiments.Length; t++)
        {
            Experiment tmp = experiments[t];
            int r = Random.Range(t, experiments.Length);
            experiments[t] = experiments[r];
            experiments[r] = tmp;
        }
    }
}
