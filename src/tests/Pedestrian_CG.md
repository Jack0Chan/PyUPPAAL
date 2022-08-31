```mermaid
graph TD
Cars
TrafficLights
LV1Pedestrian2
Cars--cWantCrss-->TrafficLights
TrafficLights--cRed-->Cars
TrafficLights--cGreen-->Cars
TrafficLights--cYellow-->Cars
LV1Pedestrian2--pCrss-->Cars
LV1Pedestrian2--pFinish-->Cars
TrafficLights--pRed-->LV1Pedestrian2
TrafficLights--pYellow-->LV1Pedestrian2
TrafficLights--pGreen-->LV1Pedestrian2
LV1Pedestrian2--pWantCrss-->TrafficLights```