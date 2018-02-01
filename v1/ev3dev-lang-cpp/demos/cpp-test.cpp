#include "ev3dev.h"

#include <thread>
#include <chrono>
#include <iostream>
#include <fstream>


using namespace ev3dev;
using namespace std;

/* OUTPUT_B[] >> Moteur B
 * OUTPUT_C[] >> Moteur C 
*/



std::ostream& operator<<(std::ostream &os, const std::set<std::string> &ss) {
  os << "[ ";
  for(const auto &s : ss) os << s << " ";
  return os << "]";
}


int main() {
    large_motor _motor_left(OUTPUT_A);
    large_motor _motor_right(OUTPUT_D);
    _motor_left.set_speed_sp(10);
    _motor_right.set_speed_sp(10);
    sound::speak("Hello world!", true);
    _motor_left.run_forever();
    _motor_right.run_forever();
   
    //large_motor  moteurC (OUTPUT_D); 
    //sound::speak("Hello world!", true);
  
    //moteurC.run_direct();
    //sound::speak("Hello world!", true);
    //moteurB.set_time_sp(50).run_timed();
    //moteurC.set_time_sp(50).run_timed();
    // moteurB.run_direct(); 
    //moteurC.run_direct();
    return 0;
}
