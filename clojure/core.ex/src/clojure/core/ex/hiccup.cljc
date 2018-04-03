(ns clojure.core.ex.hiccup)

(defn- hiccup2clojure
  [result list-map-acc hiccup]
  (loop [rst result acc list-map-acc hic hiccup] 
    (if-let [ele (first hic)]
      (cond (map? ele) (recur (conj rst ele) acc (next hic))
           ; (nil? ele) (recur rst acc (next hic))
            (vector? ele) (let [fst-e (first ele)
                                ele (if (fn? fst-e)
                                      (apply fst-e (next ele))
                                      ele)
                                kw (first ele)
                                kw (if (keyword? kw)
                                     kw
                                     (throw (Exception. (str "None keyword in Hiccup vector. " kw))))
                                sub (hiccup2clojure {} {} (next ele))
                                exist (contains? acc kw)
                                new-list (cond exist (conj (get acc kw) sub)
                                               (vector? sub) sub
                                               :else [sub])
                                new-rst (assoc rst kw new-list)
                                new-acc (assoc acc kw new-list)]
                            (recur new-rst new-acc (next hic)))
            (or (number? ele) (string? ele))
            (let [exist (contains? acc :hiccup2clojure-default-vector)
                  new-rst (if exist
                            (conj (get acc :hiccup2clojure-default-vector) ele)
                            ele)
                  new-acc (assoc acc :hiccup2clojure-default-vector (if exist new-rst [ele]))]
              (recur new-rst new-acc (next hic)))
            (sequential? ele)
            (recur rst acc (->> hic next (concat ele) (remove nil?) vec))
            :else (throw (Exception. (str "Not support format in Hiccup. " ele))))
      rst)))

(defn hiccup2clj
  "Transits hiccup format to clojure format.
   In a other word, transits a vector to map structure.

## Paramters
* key: Hiccup element name. Not used
* content: Hiccup content sequence. The element may be:
  - [sub-element]: Hiccup format
  - {property}: Hiccup property
  - sequence: 

## Feature list
### Supports xapply for content sequence and nest sequence
For example:
  (hiccup2clj
    [:interface
      [:signal {:name \"a\"}]
      (map #(vector :name %) (range 10))
      (for [sig (range 6)]
        (list
          [:signal {:name (str \"in\" sig)}]
          [:signal {:name (str \"out\" sig)}]))])

* Supports filtering nil element
```
(hiccup2clj [:intf nil [:signal] (when false 10)])
```
Above code is same with:
```
(hiccup2clj [:intf [:signal]])
```

"
  [hic]
  (if-let [[key & content] hic]
    (hiccup2clojure {} {} (->> content (remove nil?) ))))

(defn clj2hiccup
  "Translate clojure to hiccup format."
  [kw clj]
  {:pre [(keyword? kw), (map? clj)]}
  (loop [attri {} lst clj rst []]
    (if lst
      (let [ele (first lst) k (key ele) v (val ele)]
        (cond (or (number? v) (string? v))
              (recur (assoc attri k v) (next lst) rst)
              (and (vector? v) (every? map? v))
              (recur attri (next lst)
                     (if (= [] rst)
                       (apply vector (map #(clj2hiccup k %) v))
                       (apply vector rst (map #(clj2hiccup k %) v))))
              (and (vector? v) (every? #(or (number? %) (string? %)) v))
              (recur attri (next lst) [rst (apply vector k v)] #_(xapply vector rst (apply vector k v)))
              :else (throw (Exception. (str "Invalid input format. " ele)))))
      (cond (and (= [] rst) (= {} attri)) [kw]
            (= {} attri) (apply vector kw rst)
            (= [] rst) [kw attri]
            :else (apply vector kw attri rst)))))
