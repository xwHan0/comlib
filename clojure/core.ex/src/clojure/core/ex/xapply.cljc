(ns clojure.core.ex.xapply)

(defn- xapply-configure [ocfg ncfg cfg-tmp]
  {:pre [(map? ncfg) (every? #(contains? cfg-tmp %) (keys ncfg))]}
  (apply conj ocfg ncfg))

(defn- xapply-map-seq [m]
  (loop [rst []
         s m]
    (if rst
      (recur (conj (conj rst (first s)) (second s)) (nnext s))
      rst)))

(defn xapply
  "Format:
     (xapply func eles)
       eles ::=  :cfg cfg-map
                |:scalar ele1 ele2 ...
                |:sequence seq1 seq2 ...
                |:json-like scalar seq ...
   * cfg-map: A map structure for configure of xapply. Supports below feature:
        :ignore-nil?
        :ignore-empty-vector?
        :ignore-empty-map?"
  ([func & args]
   (loop [rst []
          lst args
          status :scalar
          cfg {:ignore-nil? true :ignore-empty-vector? true :ignore-empty-map? true}]
     (if lst
       (let [arg (first lst)
             rst (vec rst)]
         (cond (#{:scalar :sequence :hash-map :hash-map-vec :json-like} arg)
                 (recur rst (next lst) arg cfg)
               (= arg :cfg) 
                 (recur rst (-> lst next next) status (xapply-configure cfg (-> lst next first) cfg))
               (and (nil? arg) (:ignore-nil? cfg))
                 (recur rst (next lst) status cfg)
               (= status :sequence)
                 (cond (or (sequential? arg) (nil? arg)) 
                         (recur (concat rst arg) (next lst) status cfg)
                     (map? arg) (recur (concat (xapply-map-seq arg)) (next lst) status cfg)
                     :else (throw (Exception. (str "Invalid parameter for :sequence." arg))))
               (= status :scalar)       ;Scalar process
                (if (and (nil? arg) (:ignore-nil? cfg))     ;nil scalar process
                  (recur rst (next lst) status cfg)
                  (recur (conj rst arg) (next lst) status cfg))
               (= status :hash-map)
                 (when (map? arg)
                   (recur (apply conj rst arg) (next lst) status cfg))
               (= status :hash-map-vec)
                 (when (map? arg)
                   (recur (concat rst (vec arg)) (next lst) status cfg))
               (= status :json-like)
                 (cond
                   (sequential? arg) 
                     (recur (concat rst arg) (next lst) status cfg)
                   ;(or (number? arg) (string? arg) (map? arg)) 
                   :else
                     (if (and (nil? arg) (:ignore-nil? cfg))     ;nil scalar process
                       (recur rst (next lst) status cfg)
                       (recur (conj rst arg) (next lst) status cfg))
                   ;:else
                    ; (throw (Exception. (str "Not json format!")))
                 )
             ))
       (apply func rst)))))
