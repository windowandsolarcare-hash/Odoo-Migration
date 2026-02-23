graph TD
    subgraph OUTBOUND ENGINE: Sending the Reactivation SMS
        A[👨‍💼 Odoo User] -- 1. Clicks 'LAUNCH' --> B[⚙️ Odoo Server Action];
        B -- 2. Creates Opportunity --> C(db: Opportunity);
        B -- 3. Webhook --> D{⚡️ Zap 1: Outbound};
        D -- 4. Get Data & Post to Chatter --> C;
        D -- 5. Get Historical Job --> W_API[Workiz API];
        W_API -- 6. Create Graveyard Job --> W1[📝 Workiz Graveyard Job];
        D -- 7. Update Status (Sends SMS) --> W1;
        W1 -- 8. SMS Sent --> G([📱 Customer]);
        D -- 9. Update Opportunity w/ Link --> C;
    end

    subgraph INBOUND ENGINE: Booking & Sales Order Creation
        G2([📱 Customer]) -- 10. Books Appointment --> CAL(📅 Cal.com);
        CAL -- 11. Webhook --> J{⚡️ Zap 2: Inbound};
        
        J -- 12. Get Opportunity Details --> C;
        J -- 13. Promote Graveyard Job --> W2[✅ Workiz Live Job];
        W1 --> W2;
        
        subgraph Odoo
            C_WON(db: Opportunity 'Won');
            SO[🧾 Sales Order Created];
        end

        J -- 14. Mark Opportunity as 'Won' --> C_WON;
        C --> C_WON;
        
        %% --- THIS IS THE CORRECTION ---
        J -- 15. Create Odoo Sales Order --> SO;
        %% --- END CORRECTION ---
    end

    %% Styling
    style A fill:#875A7B,stroke:#333,stroke-width:2px,color:#fff
    style G fill:#4CAF50,stroke:#333,stroke-width:2px,color:#fff
    style G2 fill:#4CAF50,stroke:#333,stroke-width:2px,color:#fff
    style C fill:#D6D6D6,stroke:#333,stroke-width:1px,color:#000
    style W1 fill:#D6D6D6,stroke:#333,stroke-width:1px,color:#000
    style W_API fill:#FF6F61,stroke:#333,stroke-width:2px,color:#fff
    style CAL fill:#2196F3,stroke:#333,stroke-width:2px,color:#fff
    style D fill:#FF4A00,stroke:#333,stroke-width:2px,color:#fff
    style J fill:#FF4A00,stroke:#333,stroke-width:2px,color:#fff
    style B fill:#875A7B,stroke:#333,stroke-width:2px,color:#fff
    style W2 fill:#4CAF50,stroke:#333,stroke-width:2px,color:#fff
    style C_WON fill:#4CAF50,stroke:#333,stroke-width:2px,color:#fff
    style SO fill:#4CAF50,stroke:#333,stroke-width:2px,color:#fff