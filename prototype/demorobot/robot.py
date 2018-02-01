from ev3dev.auto import *

import math
import random

class Robot:
    rayon_roue_m = 0
    dist_roues_pointRot_m = 0
    moteurs = []
    capteurCouleur = ColorSensor(INPUT_1)
    lcd = Screen()
    distancesLues = []
    taille_historique = 3
    couleurCible = [0,0,0]
    sonar = UltrasonicSensor(INPUT_2)
    distanceSol = 0
    touch = TouchSensor(INPUT_4)
    boutonOff = TouchSensor(INPUT_3)
    moteurDetect = MediumMotor(OUTPUT_B)

    def __init__(self, rayon_roue_cm, dist_roues_pointRot_cm):
        Sound.speak('Hello world').wait()
        self.rayon_roue_m = rayon_roue_cm / 100.0
        self.dist_roues_pointRot_m = dist_roues_pointRot_cm / 100.0
        self.moteurs.append( LargeMotor(OUTPUT_A) ) # Gauche
        self.moteurs.append( LargeMotor(OUTPUT_D) ) # Droite
        self.lcd = Screen()
        self.lcd.clear()
        self.debugPrint("Hello world!")
        self.initDistanceSol = self.sonar.distance_centimeters

    def avancer(self, distance_metre):
        nb_tours = distance_metre / (self.rayon_roue_m * math.pi * 2.00)
        temps_ms = nb_tours * 1000.0
        for moteur in self.moteurs:
            moteur.stop_action = 'brake'
            moteur.run_timed(time_sp=temps_ms, speed_sp=360)
        time.sleep(temps_ms / 1000.0)

    def reculer(self, distance_metre):
        nb_tours = distance_metre / (self.rayon_roue_m * math.pi * 2.00)
        temps_ms = nb_tours * 1000.0
        for moteur in self.moteurs:
            moteur.stop_action = 'brake'
            moteur.run_timed(time_sp=temps_ms, speed_sp=-360)
        time.sleep(temps_ms / 1000.0)

    def moteurGauche(self):
        return self.moteurs[0]

    def moteurDroit(self):
        return self.moteurs[1]


    # Tourner ve   rs la droite. Si angle_degres est negatif, tourne vers la gauche.
    def tourner(self, angle_degres, facteurVitesse = 1.0):
        total_circon_m = (self.dist_roues_pointRot_m * math.pi * 2.00)
        dist_m_pour_degres = (abs(angle_degres) / 360.0) * total_circon_m
        nb_tours = dist_m_pour_degres / (self.rayon_roue_m * math.pi * 2.00)
        temps_ms = nb_tours * 1000.0
        moteurPositif = self.moteurGauche()
        moteurNegatif = self.moteurDroit()
        if angle_degres < 0:
            moteurPositif = self.moteurDroit()
            moteurNegatif = self.moteurGauche()
        moteurPositif.stop_action = 'brake'
        moteurNegatif.stop_action = 'brake'
        moteurNegatif.run_timed(time_sp=temps_ms, speed_sp=-360*facteurVitesse)
        moteurPositif.run_timed(time_sp=temps_ms, speed_sp=360*facteurVitesse)
        time.sleep(temps_ms / 1000.0)

    def debugPrint(self, txt):
        print(txt)
#        self.lcd.draw.text( (0,0), txt )
#        self.lcd.update()

    def CouleurToStr(self, couleur):
        return '('+str(couleur[0]) + ' , ' + str(couleur[1]) + ' , ' + str(couleur[2])+')'

    def AutomateModeRaw(self):
        self.couleurCible = self.capteurCouleur.raw
        couleurLue = self.capteurCouleur.raw
        distancePassee = self.lireDistance(couleurLue)
        print( 'Couleur cible = ' + self.CouleurToStr(self.couleurCible) )
        print( 'Couleur initialement lue = ' + self.CouleurToStr(couleurLue) )
        print( 'Distance initiale = ' + str(distancePassee) )
        Mult = 1
        while not self.estRouge( couleurLue ):
            distance = self.lireDistance(couleurLue)
            self.afficherLCD(self.couleurCible, couleurLue, distance)
            valabsolueDistance = math.fabs(distance - distancePassee)
            print('Couleur lue = ' + self.CouleurToStr(couleurLue))
            if valabsolueDistance < 1.5:
                print ("J'avance, valeur absolue distance = " + str(valabsolueDistance) )
                self.avancer(0.05)
            else:
                if distance > distancePassee:

                    Mult *= -1
                    print("Je tourne, " + str(Mult) + ", valeur absolue distance = " + str(valabsolueDistance))
                    distancePassee = distance
                self.tourner(Mult, 1)
            couleurLue = self.capteurCouleur.raw

    def testTouch(self):
        while True:
            if self.touch.is_pressed:
                break
            self.avancer(0.01)

    def avancerForever(self):
        for moteur in self.moteurs:
            moteur.stop_action = 'brake'
            moteur.run_forever(speed_sp=360)

    def testTable(self):
        self.avancerForever()
        while not self.boutonOff.is_pressed:
            distanceSol = self.sonar.distance_centimeters   # millimetres
            if ( distanceSol >= ( 2.0 * self.initDistanceSol) ) or self.touch.is_pressed:
                self.stop()
                Sound.play('r2d2-audio-hd.wav').wait()
                self.reculerX()
                rotDirection = 1
                if random.randint(0, 1) == 1:
                    rotDirection = -1
                self.tourner( rotDirection * random.randint(30, 60))
                self.avancerForever()
        self.stop()

    def stop(self):
        for moteur in self.moteurs:
            moteur.stop_action = 'brake'
            moteur.stop()

    def reculerX(self):
        cherche = True
        for moteur in self.moteurs:
            moteur.stop_action = 'brake'
            moteur.run_forever(speed_sp=-360)
        couleurLue = self.capteurCouleur.raw
        direction = 1
        self.moteurDetect.run_forever(speed_sp=direction * 180)
        while (not self.estNoir(couleurLue)) and (not self.boutonOff.is_pressed):
            couleurLue = self.capteurCouleur.raw
            self.debugPrint( self.CouleurToStr(couleurLue))
            if cherche and self.estRouge(couleurLue):
                direction *= -1
                self.moteurDetect.stop()
                self.moteurDetect.run_forever(speed_sp=direction * 180)
                cherche = False
            elif not self.estRouge( couleurLue ):
                cherche = True
        self.moteurDetect.stop()
        self.stop()

    def demiTour(self):
        self.reculerX()
       # self.tourner(180,1)

    def testSonar(self):
        while True:
            distanceSol = self.sonar.distance_centimeters   # millimetres
            self.debugPrint(str( distanceSol * 0.1) + " cm")
            if distanceSol >= ( 2.0 * self.initDistanceSol):
                break
            self.avancer(0.01)

    def lireDistance(self, couleurLue):
        distance = self.calculerDistance(self.couleurCible, couleurLue)
        return distance
#        self.ajouterDistanceDansHistorique(distance)
#        if len(self.distancesLues) > 0:
#            return sum(self.distancesLues)/len(self.distancesLues);
#        else:
#            return 0

    def ajouterDistanceDansHistorique(self, distance):
        if len(self.distancesLues) == self.taille_historique:
            self.distancesLues.pop( 0 )
        self.distancesLues.append( distance )

    def estRouge(self, couleur):
        return ((couleur[0] > 90) and (couleur[1] < 50) and (couleur[2] < 50))

    def estNoir(self, couleur):
        return ((couleur[0] < 20) and (couleur[1] < 20) and (couleur[2] < 20))

    def afficherLCD(self, txt):
        self.lcd.clear()
        self.lcd.draw.text((0, 0), txt )
        self.lcd.update()

    def calculerDistance(self, couleurCible, couleurLue):
# euclid return math.sqrt((couleurCible[0]-couleurLue[0])**2 +(couleurCible[1]-couleurLue[1])**2 +(couleurCible[2]-couleurLue[2])**2)
        return math.fabs(couleurCible[0]-couleurLue[0]) + math.fabs(couleurCible[1]-couleurLue[1]) + math.fabs(couleurCible[2]-couleurLue[2])
