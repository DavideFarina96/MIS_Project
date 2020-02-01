using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Experiment
{
    public GameObject path;
    public enums.FeedbackTypes feedback;
    public int repetitionNumber;

    public Experiment(GameObject path, enums.FeedbackTypes fbtype, int repetitionNumber)
    {
        this.path = path;
        this.feedback = fbtype;
        this.repetitionNumber = repetitionNumber;
    }

    override
    public string ToString()
    {
        return path.name + "_" + feedback + "_" + repetitionNumber;
    }
}
