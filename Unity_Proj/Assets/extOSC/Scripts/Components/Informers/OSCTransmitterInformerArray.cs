/* Copyright (c) 2019 ExT (V.Sigalkin) */

using UnityEngine;

using System.Collections.Generic;

namespace extOSC.Components.Informers
{
    [AddComponentMenu("extOSC/Components/Transmitter/Array Informer")]
    public class OSCTransmitterInformerArray : OSCTransmitterInformer<List<OSCValue>>
    {
        #region Protected Methods

        protected override void FillMessage(OSCMessage message, List<OSCValue> value)
        {
            int[] nesw = new int[4];

            for (int i = 0; i < value.Count; i++)
            {
                nesw[i] = value[i].IntValue;
            }

            message.AddValue(OSCValue.String(string.Join("_", nesw)));

            //message.AddValue(OSCValue.Array(value.ToArray()));
        }

        #endregion
    }
}