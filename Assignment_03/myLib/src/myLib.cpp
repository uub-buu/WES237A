//
//  myLib.cpp
//  Lab4
//
//  Created by Alireza on 2/14/20.
//  Copyright Â© 2020 Alireza. All rights reserved.
//
#include <cstdint>
#include "myLib.h"
#include "cycletime.h"

extern "C" unsigned int cycle_count(void){
    return get_cyclecount();
}

extern "C" void inititialize(int32_t do_reset, int32_t enable_divider){
    init_counters(do_reset, enable_divider);
}


