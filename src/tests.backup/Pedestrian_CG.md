```mermaid
graph TD
Cars--cWantCrss-->TrafficLights
TrafficLights--cGreen,cRed,cYellow-->Cars
LV1Pedestrian2--pCrss,pFinish-->Cars
TrafficLights--pGreen,pRed,pYellow-->LV1Pedestrian2
LV1Pedestrian2--pWantCrss-->TrafficLights
```