# Refund Decision Flow

---

## Node: D1  
**Type:** Decision  
**Question:** Is the returned amount foreign currency?  
**Context:** Determine if refund currency is AUD or foreign. Check original payment.  

### Paths:

#### YES

- **Node:** Attach SC/LC  
  **Type:** Action  
  **Tool:** Intellimatch  
  **Description:** Attach Settlement Copy (SC), Letter of Credit (LC), and any Supporting Documents (SDs)  
  **Documents:**  
  - SC: Settlement Copy of returned payment (`CBA-TXN-20251002-001`)  
  - LC: Letter of Credit (`CBA-LC-20251002-R`)  

  - **Next Node:** D2  
    **Type:** Decision  
    **Question:** Was the nostro item found?  
    **Instructions:** Check `Pacs.008`, `Pacs.004`, and `MT940`  

    ##### Paths:

    ###### YES

    - **Node:** D3  
      **Type:** Decision  
      **Question:** Are we refunding the FCA?  
      **Instructions:** Check account type in sample data; confirm FCA account type  

      ####### Paths:

      ######## YES

      - **Node:** FCA SAME NAME  
        **Type:** Action  
        **Tool:** Internal Branch system  
        **Instructions:**  
          Ensure FCA account is same as original debited account. Attach note: `"FCA SAME NAME"`  

        - **Next:** Debit Nostro  
          **Type:** Action  
          **Tool:** Payment system  
          **Instructions:**  
            Debit Nostro account; check `MT940 :61:` and `:86:` for traceability; reference `Pacs.008/004`  

          - **Next:** Credit FCA  
            **Type:** Action  
            **Tool:** Payment system  
            **Instructions:** Update client’s FCA balance  

            - **Next:** Update SNDR Ref  
              **Type:** Action  
              **Tool:** Payment system  
              **Instructions:**  
                Use Nostro reference from MT940/return messages (`RET-USD-xxxxxx`)  

              - **Next:** D5  
                **Type:** Decision  
                **Question:** Is Markets?  
                **Instructions:** POC default is NO  

                ########## Paths:

                - **YES:**  
                  - **Node:** Send Refund FCA Email  
                    **Type:** Action  
                    **Tool:** Document Copy  
                    **Saved_Name:** 56  
                    - **Next:** Update QF  

                - **NO:**  
                  - **Node:** Send Refund (Daily List/Full List)  
                    **Type:** Action  
                    **Tool:** Document Copy  
                    **Saved_Name:** 26  
                    - **Next:** Update QF  

                - **Converge:** Submit Case to Closed

      ######## NO

      - **Node:** Debit Nostro Payment Input Screen  
        **Type:** Action  
        **Tool:** Payment system  
        **Instructions:** Payment input screen per SOP  

        - **Next:** Update SNDR Ref  
          **Type:** Action  
          **Tool:** Payment system  
          **Instructions:**  
            Reference Nostro item as per `Pacs.008/004` and `MT940`  
          - **Next:** D7

    ###### NO

    - **Node:** Disposition waiting for SCR  
      **Type:** Action  
      **Tool:** CaseTool  
      **Instructions:** Add note with current date; awaiting SCR  

      - **Next:** D4  
        **Type:** Decision  
        **Question:** Was the nostro item found?  
        **Instructions:** Check `Pacs.008/004`, `MT940`  

        ####### Paths:

        - **YES:**  
          - **Node:** Attach SC/LC  
            **Type:** Action  
            **Tool:** Intellimatch  
            - **Next:** D3

        - **NO:**  
          - **Node:** Send Nostro Not Credited  
            **Type:** Action  
            **Tool:** Document Copy  
            **Saved_Name:** 39  
            - **Next:** D7

#### NO

- **Node:** D6  
  **Type:** Decision  
  **Question:** Vostro bank has given debit authority?  
  **Instructions:** Request `Camt.029` for debit authority; check Vostro sheets  

  ##### Paths:

  - **YES:**  
    - **Node:** Debit Vostro Payment Input Screen  
      **Type:** Action  
      **Tool:** Payment system  
      **Instructions:** Debit Vostro using approved `Camt.029` response  

      - **Next:** SNDR Ref being Vostro bank's case reference  
        **Type:** Action  
        **Tool:** Payment system  
        **Instructions:** Record reference as returned in `Pacs.004`  
        - **Next:** D7

  - **NO:**  
    - **Node:** Funds in OB  
      **Type:** Action  
      **Tool:** CaseTool  
      **Instructions:** Check OB accounts  

      - **Next:** Debit OB Payment Input Screen  
        **Type:** Action  
        **Tool:** Payment system  

        - **Next:** SNDR Ref being CBA case reference without letters  
          **Type:** Action  
          **Tool:** Payment system  
          **Instructions:** Use OB reference  
          - **Next:** D7

---

## Node: D7  
**Type:** Decision  
**Question:** Is this a Branch payment?  

### Paths:

- **YES:**  
  - **Node:** Credit Branch SAIT  
    **Type:** Action  
    **Tool:** Payment system  
    **Instructions:**  
      Account number changes to branch SAIT (`4-digit BSB + 0001195062`)  
    - **Next:** D8

- **NO:**  
  - **Node:** Credit Client Original Debited Account  
    **Type:** Action  
    **Tool:** Payment system  
    - **Next:** D8

---

## Node: D8  
**Type:** Decision  
**Question:** Is Markets?

### Paths:

- **YES:**  
  - **Node:** Send Refund Sent Email  
    **Type:** Action  
    **Tool:** Document Copy  
    **Saved_Name:** 67  
    - **Next:** Update QF

- **NO:**  
  - **Node:** D9  
    **Type:** Decision  
    **Question:** Does client have valid email address?  

    #### Paths:

    - **YES:**  
      - **Node:** Send Refund (Daily List/Full List)  
        **Type:** Action  
        **Tool:** Document Copy  
        **Saved_Name:** 26  
        - **Next:** Update QF

    - **NO:**  
      - **Node:** Send the client an AdHoc  
        **Type:** Action  
        **Tool:** Internal Branch system  

        - **Next:** Send Refund NO email (Full List) to CBA Reports  
          **Type:** Action  
          **Tool:** Document Copy  
          **Saved_Name:** 19  
          - **Next:** Update QF

---

## Node: Update QF  
**Type:** Action  
**Tool:** CaseTool  
**Instructions:** Update QF screen as per SOP  
- **Next:** Submit Case to Closed

---

## Node: Submit Case to Closed  
**Type:** End  
**Description:** END OF THE PROCESS