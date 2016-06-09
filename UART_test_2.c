#include <device.h>

#define RX_BUFFER_LEN 64; 

void main()
{

    CYGlobalIntEnable;
    uint32 rxData;
    char headerString[590];
    char lineString[590];
    char sendString[64];
    int mainloopcount = 0;
    int innerloopcount = 0;
//    const char whitespace[2] = " ";
    
    /* Initialize the char LCD and display "Hello" */
	LCD_Char_Start();
//	LCD_Char_PrintString("Hello");
	
	/* Initialize UART */
    UART_Start();

    for(;;)
    {
        mainloopcount++;
        memset(headerString, '\0', sizeof(headerString));
        memset(lineString, '\0', sizeof(lineString));
        memset(sendString, '\0', sizeof(sendString));

        LCD_Char_ClearDisplay();
        LCD_Char_Position(0,0);
        LCD_Char_PrintString("Hello");
            
        sprintf(sendString, "0,MEID12345\r\n");
	    UART_PutString(sendString);
        CyDelay(100u);
    
        int response = 0;
        
        while(!response) {
            rxData = UART_GetChar();
            
            if(rxData) {
                response = 1;
            }
                
            }
        
        // Read header
        if(rxData) { // make sure data is non-zero
//            UART_ClearTxBuffer();
            innerloopcount++;
            LCD_Char_ClearDisplay();
            LCD_Char_Position(0,0);
            LCD_Char_PrintString("Enter if");
            
            // Fill in headerString
            sprintf(headerString, "%c", rxData);            
            int i;
            for(i = 0; i < 64; i++) {
                CyDelay(100u);
                rxData = UART_GetChar();
                sprintf(headerString, "%s%c", headerString, rxData);
                if(rxData == 10 || rxData == 0) {
                break;
                }
            }
                        
            CyDelay(200u);
            int numLines;
            // Parse header string
            sscanf(headerString, "%d %s", numLines, lineString); // numLines isn't filling
            CyDelay(100u);
            
            CyDelay(100u);
            LCD_Char_ClearDisplay();
            LCD_Char_Position(0,0);
            LCD_Char_PrintString(lineString);
            
            int lineNum;
            // Read each line over UART
            for(lineNum = 1; lineNum < 347; lineNum++) {
                memset(lineString, '\0', sizeof(lineString));
                memset(sendString, '\0', sizeof(sendString));
                
                CyDelay(100u);
                sprintf(sendString, "%d\r\n", lineNum);
                
	            UART_PutString(sendString);
                
                CyDelay(200u);
                
                rxData = UART_GetChar();
                if(rxData == 58) { // make sure first character is colon
                
                LCD_Char_ClearDisplay();
                LCD_Char_Position(0,0);
                LCD_Char_PrintString("Enter line");
                
                // Fill in lineString
                sprintf(lineString, "%c", rxData);            
                
                for(i = 1; i < 590; i++) {
                rxData = UART_GetChar();
                sprintf(lineString, "%s%c", lineString, rxData);
                
                CyDelay(100u);

                char LCD_String[16];
                sprintf(LCD_String, "%d %d %c", lineNum, i, rxData);
                LCD_Char_ClearDisplay();
                LCD_Char_Position(0,0);
                LCD_Char_PrintString(LCD_String);
                LED_Blue_Write( !LED_Blue_Read() );
                

                
                if(rxData == 10 || rxData == 0) {
                break;
                }
            }
//                LCD_Char_ClearDisplay();
//                LCD_Char_Position(0,0);
//                LCD_Char_PrintString(lineString);
//                LED_Blue_Write( !LED_Blue_Read() );
            // here's where linestring can be seen
            //
            }
            
        }
        
//        UART_ClearRxBuffer();
    }
}
}

/* [] END OF FILE */
