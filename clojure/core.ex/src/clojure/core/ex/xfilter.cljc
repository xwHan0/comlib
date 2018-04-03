(ns clojure.core.ex.xfilter)

(defn- get-cfg [default & arg]
  (loop [rst default lst arg]
    (if (keyword? (first lst))
      (recur 
        (assoc rst (first lst) (second lst))
        (nnext lst))
      [rst lst])))

(defn xfilter [& args]
"
# Syntax: 
  (xfilter & cfg-map-pair & colls)
# Parameter:
* cfg-map-pair ::= cfg-key cfg-value
** cfg-key ::= 
***            :st  Start condition (Include)
***            :ed  End condition (Exclude)
***            :n   Max number of result
***            :pred filter condition: (p1 p2...)=>pred?
***     where the parameter number of st, ed and pred is same with (count of colls)
* colls   
    
"
  (letfn [
    (xf [{:keys [st ed n pred]} colls]
      (loop [status :IDLE
             num n
             cs colls
             rst []]
        (if cs
          (let [f (first cs)]
            (case status
              :IDLE (if (apply st f)
                      (recur :NORM num cs rst)
                      (recur :IDLE num (next cs) rst))
              :NORM (cond 
                      (<= num 0) rst
                      (apply ed f) rst
                      (apply pred f)
                        (recur status (dec num) (next cs) (conj rst f))
                      :else 
                        (recur status num (next cs) rst))))
           rst)))
    ]
    (let [[{:keys [rst] :as cfg} lst] 
            (apply get-cfg {:st (constantly true) 
                            :ed (constantly false) 
                            :pred (constantly true)
                            :rst first
                            :n 999999999} args)
          colls (apply map vector lst)
          result (xf cfg colls)]
      (map rst result))))
