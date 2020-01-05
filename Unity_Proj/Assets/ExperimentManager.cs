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
    public int currentFeedbackType = 0;

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
        if(isStarted)
        {
            //Debug.Log("Current Phase: " + currentPhase);
            switch(currentPhase)
            {
                case enums.ExperimentPhases.PREPARING:
                    //Debug.Log("Now running experiment number " + currentExperimentNumber);
                    experiments[currentExperimentNumber].path.SetActive(true);
                    currentFeedbackType = (int)experiments[currentExperimentNumber].feedback;
                    textFieldComp.text = "Move your cursor near the blue ball to begin."; break;
                case enums.ExperimentPhases.RUNNING:
                    textFieldComp.text = "Follow the blue ball"; break;
                case enums.ExperimentPhases.FINISHED:
                    experiments[currentExperimentNumber].path.SetActive(false);
                    currentExperimentNumber++;
                    currentPhase = enums.ExperimentPhases.PREPARING; break;
            }            
        }
    }

    void GenerateExperimentsList()
    {
        //Generate the sequence of experiments
        Experiment[] tempExperiments = new Experiment[paths.Length * FeedbackTypesLength];

        for (int i = 0; i < paths.Length; i++)
        {
            for (int j = 0; j < FeedbackTypesLength; j++)
            {
                int index = i * FeedbackTypesLength + j;
                tempExperiments[index] = new Experiment(paths[i], (enums.FeedbackTypes)j, 0);
            }
        }

        // Shuffle the experiments around
        Shuffle(tempExperiments);
        experiments = new Experiment[tempExperiments.Length * repetitionsPerPath];
        for (int i = 0; i < tempExperiments.Length; i++)
        {
            for (int j = 0; j < repetitionsPerPath; j++)
            {
                int index = i * repetitionsPerPath + j;
                experiments[index] = new Experiment(tempExperiments[i].path, tempExperiments[i].feedback, j + 1);
            }
        }
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
