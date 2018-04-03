(ns clojure.core.ex.concat-distinct)

(defn- another-coll-distinct [coll coll-set]
  (loop [rst [] lst coll]
    (if lst
      (let [f (first lst)]
        (recur (if (coll-set f) rst (conj rst f)) (next lst)))
      (vec rst))))

(defn concat-distinct [coll1 coll2 & {:keys [select-first?] :or {select-first? true}}]
"
** select-first? : 
"
  (let [coll-base (if select-first? coll1 coll2)
        coll-base (-> coll-base distinct vec)
        coll-base-set (set coll-base)]
    (into coll-base (another-coll-distinct (if select-first? coll2 coll1) coll-base-set))))