//
//  myLib.h
//  Lab2
//
//  Created by Alireza on 7/6/16.
//  Copyright © 2016 Alireza. All rights reserved.
//

#ifndef myLib_h
#define myLib_h

#ifdef __cplusplus
extern "C" {
#endif
    
unsigned int cycle_count(void);
void inititialize(int32_t do_reset, int32_t enable_divider);

#ifdef __cplusplus
}
#endif

#endif /* myLib_h */
