#include <device.h>

#define RX_BUFFER_LEN 64; 

void main()
{

    CYGlobalIntEnable;
    uint32 rxData;
//    char rxChar = rxData;
    char recvString[16];
    char sendString[64];
    /* Initialize the char LCD and display "Hello" */
	LCD_Char_Start();
	LCD_Char_PrintString("Hello");
	
	/* Display the instruction to the user on how to start bootloading */
	//LCD_Char_Position(1,0);
	//LCD_Char_PrintString("SW1-P6.1 to BL");

	/* Initialize PWM */
    UART_Start();
	
	/* CyBtldr_Start() API does not return – it ends with a software device reset. So, the code 
	   after this API call (below) is never executed. */
    for(;;)
    {
        memset(recvString, '\0', sizeof(recvString));
        memset(sendString, '\0', sizeof(sendString));
        
        rxData = UART_GetChar(); // store received characters in temporary variable

        if(rxData) { // make sure data is non-zero
            sprintf(recvString, "%c", rxData);
            
            int i;
            for(i = 1; i < 16; i++) {
                CyDelay(200u);
                rxData = UART_GetChar();
                sprintf(recvString, "%s%c", recvString, rxData);
                if(rxData == 10 || rxData == 0) {
                break;
                }
                
            }
            
            LCD_Char_ClearDisplay();
            LCD_Char_Position(0,0);
            LCD_Char_PrintString(recvString);
            LED_Blue_Write( !LED_Blue_Read() );
 
            // Handle received characters
            CyDelay(200u);
            sprintf(sendString, "0 %s\r\n", recvString);
            UART_PutString(sendString);

            
        }
        
//        UART_ClearRxBuffer();
    }
}

/* [] END OF FILE */
